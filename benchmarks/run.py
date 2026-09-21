"""
Routing benchmark: does execution history actually improve agent selection?

Four strategies run over the same task stream:

  oracle      always picks the genuinely best agent — the achievable ceiling
  horizon      full router, records every outcome and learns from it
  capability  same router, but never told what happened (cold-start forever)
  random      uniform choice — the floor

`capability` is the honest comparison. It isolates the contribution of the
feedback loop, because it is the identical system minus the learning.

Runs against a live PostgreSQL with pgvector. The default embedding provider is
offline and deterministic, so the headline numbers cost nothing to reproduce.

    python -m benchmarks.run --tasks 1000 --seed 42
    python -m benchmarks.run --tasks 1000 --repeat 5          # spread across seeds
    python -m benchmarks.run --phrasing paraphrase            # no lexical shortcut
    python -m benchmarks.run --embeddings openai              # real model (costs money)
"""

import argparse
import asyncio
import json
import os
import pathlib
import random
import statistics
import sys
import time
from dataclasses import dataclass, field

RESULTS_PATH = pathlib.Path("benchmarks/results.json")
REPEATS_PATH = pathlib.Path("benchmarks/repeats.json")

STRATEGIES = ("oracle", "horizon", "capability", "random")


@dataclass
class StrategyRun:
    name: str
    successes: list[int] = field(default_factory=list)
    costs: list[float] = field(default_factory=list)
    picks: list[str] = field(default_factory=list)
    families: list[str] = field(default_factory=list)
    confidences: list[float] = field(default_factory=list)

    def record(self, success: bool, cost: float, agent: str, family: str, conf: float = 0.0):
        self.successes.append(1 if success else 0)
        self.costs.append(cost)
        self.picks.append(agent)
        self.families.append(family)
        self.confidences.append(conf)

    @property
    def accuracy(self) -> float:
        return statistics.mean(self.successes) if self.successes else 0.0

    def rolling(self, window: int) -> list[float]:
        out, run = [], 0
        for i, s in enumerate(self.successes):
            run += s
            if i >= window:
                run -= self.successes[i - window]
            out.append(run / min(i + 1, window))
        return out

    def cost_per_success(self) -> float:
        wins = sum(self.successes)
        return sum(self.costs) / wins if wins else float("inf")

    def final_accuracy(self, tail: int) -> float:
        tail_slice = self.successes[-tail:] or self.successes
        return statistics.mean(tail_slice)


def _family_accuracy(run: StrategyRun, family: str, tail: int) -> float:
    """Accuracy on one family over the final `tail` tasks of that family."""
    hits = [s for s, fam in zip(run.successes, run.families, strict=True) if fam == family]
    return statistics.mean(hits[-tail:] or [0])


async def _signup(client, email: str):
    resp = await client.post("/v1/organizations", json={"name": email, "email": email})
    resp.raise_for_status()
    body = resp.json()
    return {"Authorization": f"Bearer {body['api_key']}"}


async def _register_agents(client, headers) -> dict[str, str]:
    from benchmarks.world import AGENTS

    ids = {}
    for spec in AGENTS:
        resp = await client.post(
            "/v1/agents",
            json={
                "name": spec.name,
                "endpoint": f"https://agents.example.com/{spec.name}",
                "description": spec.capability_text(),
                "capabilities": list(spec.declared),
                "cost_per_call_usd": spec.cost_per_call_usd,
            },
            headers=headers,
        )
        resp.raise_for_status()
        ids[spec.name] = resp.json()["id"]
    return ids


def _provider(name: str):
    """
    Pick the embedding model the run is measured under.

    `deterministic` is a hashed bag-of-words: offline, free, reproducible, and
    purely lexical. `openai` is the real thing, and the only way to know whether
    the similarity thresholds tuned against lexical overlap survive contact with
    a semantic model. It costs money and needs OPENAI_API_KEY.
    """
    from horizon.services.embeddings import DeterministicEmbeddings, OpenAIEmbeddings

    if name == "openai":
        return OpenAIEmbeddings()
    return DeterministicEmbeddings()


async def run(
    n_tasks: int,
    seed: int,
    window: int,
    *,
    embeddings: str = "deterministic",
    paraphrase: bool = False,
) -> dict:
    import httpx

    from benchmarks.world import AGENT_BY_NAME, AGENTS, FAMILIES
    from horizon.main import app
    from horizon.services import router as routing
    from horizon.services.embeddings import set_embeddings

    set_embeddings(_provider(embeddings))

    rng = random.Random(seed)
    # Common random numbers: one uniform draw per task, shared by every
    # strategy. Independent streams would let a strategy beat the oracle on
    # sampling luck alone, which is both noisy and indefensible. Sharing the
    # draw makes the comparison paired and makes the oracle a strict per-task
    # upper bound — it succeeds whenever any other strategy would.
    choice_rng = random.Random(seed + 1)

    runs = {s: StrategyRun(s) for s in STRATEGIES}
    best_for = {f.name: max(AGENTS, key=lambda a: a.competence[f.name]).name for f in FAMILIES}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://bench", timeout=60.0
    ) as client:
        horizon_h = await _signup(client, "horizon-bench@example.com")
        cap_h = await _signup(client, "capability-bench@example.com")
        horizon_ids = await _register_agents(client, horizon_h)
        await _register_agents(client, cap_h)

        started = time.monotonic()
        for i in range(n_tasks):
            family = rng.choice(FAMILIES)
            task = family.render(rng, paraphrase=paraphrase)
            draw = rng.random()

            def succeeds(agent, fam=family, u=draw) -> bool:
                return u < agent.competence[fam.name]

            # --- oracle ---
            agent = AGENT_BY_NAME[best_for[family.name]]
            runs["oracle"].record(succeeds(agent), agent.cost_per_call_usd, agent.name, family.name)

            # --- random ---
            agent = choice_rng.choice(AGENTS)
            runs["random"].record(succeeds(agent), agent.cost_per_call_usd, agent.name, family.name)

            # --- capability only (no feedback ever recorded) ---
            resp = await client.post("/v1/route", json={"task": task}, headers=cap_h)
            resp.raise_for_status()
            body = resp.json()
            agent = AGENT_BY_NAME[body["selected_agent"]["name"]]
            ok = succeeds(agent)
            runs["capability"].record(
                ok, agent.cost_per_call_usd, agent.name, family.name, body["confidence"]
            )

            # --- horizon (routes, then reports the outcome back) ---
            resp = await client.post("/v1/route", json={"task": task}, headers=horizon_h)
            resp.raise_for_status()
            body = resp.json()
            agent = AGENT_BY_NAME[body["selected_agent"]["name"]]
            ok = succeeds(agent)
            runs["horizon"].record(
                ok, agent.cost_per_call_usd, agent.name, family.name, body["confidence"]
            )

            # Report against the stored decision rather than re-sending the task.
            # This is the path a real caller takes: one embedding per task, and
            # the audit trail comes from the server's own record.
            feedback = await client.post(
                "/v1/executions",
                json={
                    "agent_id": horizon_ids[agent.name],
                    "decision_id": body["decision_id"],
                    "status": "success" if ok else "failure",
                    "latency_ms": 100,
                    "cost_usd": agent.cost_per_call_usd,
                },
                headers=horizon_h,
            )
            feedback.raise_for_status()

            if (i + 1) % 100 == 0:
                elapsed = time.monotonic() - started
                print(
                    f"  {i + 1}/{n_tasks} tasks  ({elapsed:.0f}s)  "
                    f"horizon={runs['horizon'].rolling(window)[-1]:.0%}  "
                    f"capability={runs['capability'].rolling(window)[-1]:.0%}",
                    file=sys.stderr,
                )

    tail = max(1, n_tasks // 4)
    return {
        "sql_check": await _verify_from_sql(tail),
        "config": {
            "tasks": n_tasks,
            "seed": seed,
            "window": window,
            "tail": tail,
            "embeddings": embeddings,
            "phrasing": "paraphrase" if paraphrase else "template",
            "evidence_min_similarity": routing.EVIDENCE_MIN_SIMILARITY,
        },
        "strategies": {
            name: {
                "overall_accuracy": r.accuracy,
                "final_accuracy": r.final_accuracy(tail),
                "cost_per_success": r.cost_per_success(),
                "total_cost": sum(r.costs),
                "rolling": r.rolling(window),
                "pick_distribution": {a.name: r.picks.count(a.name) / len(r.picks) for a in AGENTS},
                "mean_confidence_tail": (
                    statistics.mean(r.confidences[-tail:]) if any(r.confidences) else None
                ),
            }
            for name, r in runs.items()
        },
        "per_family": {
            f.name: {name: _family_accuracy(r, f.name, tail) for name, r in runs.items()}
            for f in FAMILIES
        },
    }


async def _verify_from_sql(tail: int) -> dict:
    """
    Recompute the headline number straight from the database.

    The in-process counters above could drift from what was actually stored.
    Joining executions to their routing decisions and recomputing accuracy over
    the same tail is the check that the recorded history — the thing a customer
    would be paying for — really says what the summary table says.
    """
    from sqlalchemy import text

    from horizon.config.database import SessionLocal

    async with SessionLocal() as session:
        rows = (
            await session.execute(
                text("""
                SELECT e.status, e.followed
                FROM executions e
                JOIN routing_decisions d ON d.id = e.decision_id
                JOIN organizations o ON o.id = e.org_id
                WHERE o.email = :email
                ORDER BY e.created_at
                """),
                {"email": "horizon-bench@example.com"},
            )
        ).all()

    linked = len(rows)
    tail_rows = rows[-tail:] if linked else []
    return {
        "linked_executions": linked,
        "followed_share": (sum(1 for _, f in rows if f) / linked) if linked else 0.0,
        "final_accuracy_from_sql": (
            sum(1 for s, _ in tail_rows if s == "success") / len(tail_rows) if tail_rows else 0.0
        ),
    }


async def _reset_database() -> None:
    """Fresh slate: the point is to watch learning start from zero."""
    from sqlalchemy import text

    from horizon.config.database import SessionLocal

    async with SessionLocal() as session:
        await session.execute(
            text(
                "TRUNCATE organizations, api_keys, memories, agents, "
                "routing_decisions, executions CASCADE"
            )
        )
        await session.commit()


async def _main_async(args) -> dict:
    await _reset_database()
    return await run(
        args.tasks,
        args.seed,
        args.window,
        embeddings=args.embeddings,
        paraphrase=args.phrasing == "paraphrase",
    )


async def _repeat_async(args) -> dict:
    """
    Run consecutive seeds and report the spread.

    A single seed is one draw from a stochastic world, and the engine itself is
    not bit-reproducible either: pgvector's HNSW search is approximate, so the
    50 "most similar" past executions can differ between runs of the same seed.
    Quoting one number as if it were exact would overstate what this measures.
    """
    per_seed = []
    for i in range(args.repeat):
        seed = args.seed + i
        print(f"  seed {seed} ({i + 1}/{args.repeat})...", file=sys.stderr)
        await _reset_database()
        result = await run(
            args.tasks,
            seed,
            args.window,
            embeddings=args.embeddings,
            paraphrase=args.phrasing == "paraphrase",
        )
        per_seed.append(
            {
                "seed": seed,
                **{
                    name: {
                        "overall_accuracy": result["strategies"][name]["overall_accuracy"],
                        "final_accuracy": result["strategies"][name]["final_accuracy"],
                    }
                    for name in STRATEGIES
                },
            }
        )

    def _spread(name: str, key: str) -> dict:
        vals = [r[name][key] for r in per_seed]
        return {
            "mean": statistics.mean(vals),
            "min": min(vals),
            "max": max(vals),
            "stdev": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        }

    lifts = [r["horizon"]["final_accuracy"] - r["capability"]["final_accuracy"] for r in per_seed]
    return {
        "config": {
            "tasks": args.tasks,
            "seeds": [r["seed"] for r in per_seed],
            "embeddings": args.embeddings,
            "phrasing": args.phrasing,
        },
        "per_seed": per_seed,
        "aggregate": {
            name: {k: _spread(name, k) for k in ("overall_accuracy", "final_accuracy")}
            for name in STRATEGIES
        },
        "final_lift_over_capability": {
            "mean": statistics.mean(lifts),
            "min": min(lifts),
            "max": max(lifts),
            "stdev": statistics.stdev(lifts) if len(lifts) > 1 else 0.0,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=int, default=800)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--window", type=int, default=50, help="rolling accuracy window")
    parser.add_argument(
        "--embeddings",
        choices=("deterministic", "openai"),
        default="deterministic",
        help="embedding model to measure under; openai needs OPENAI_API_KEY and costs money",
    )
    parser.add_argument(
        "--phrasing",
        choices=("template", "paraphrase"),
        default="template",
        help="paraphrase varies the wording per task, so lexical overlap stops being a shortcut",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=0,
        help="run this many consecutive seeds and report the spread (writes repeats.json)",
    )
    args = parser.parse_args()

    from horizon import devdb

    os.environ["DATABASE_URL"] = devdb.start(
        pathlib.Path(os.environ.get("BENCH_PGDATA", "/tmp/horizon-bench-pgdata"))
    )
    os.environ.setdefault("API_KEY_PEPPER", "benchmark-pepper")

    import subprocess

    subprocess.run([".venv/bin/alembic", "upgrade", "head"], check=True, capture_output=True)

    if args.repeat:
        print(
            f"running {args.tasks} tasks x {args.repeat} seeds from {args.seed}...", file=sys.stderr
        )
        repeats = asyncio.run(_repeat_async(args))
        REPEATS_PATH.parent.mkdir(exist_ok=True)
        REPEATS_PATH.write_text(json.dumps(repeats, indent=2))
        agg = repeats["aggregate"]
        print(f"\n{'strategy':<12} {'overall (mean)':>15} {'last-quarter mean [min, max]':>32}")
        print("-" * 62)
        for name in STRATEGIES:
            o, f = agg[name]["overall_accuracy"], agg[name]["final_accuracy"]
            print(
                f"{name:<12} {o['mean']:>14.1%}  "
                f"{f['mean']:>13.1%} [{f['min']:.1%}, {f['max']:.1%}]"
            )
        lift = repeats["final_lift_over_capability"]
        print(
            f"\nlift over capability-only: {lift['mean']:+.1%} mean "
            f"(range {lift['min']:+.1%} to {lift['max']:+.1%}, sd {lift['stdev']:.1%})"
        )
        print(f"results written to {REPEATS_PATH}")
        return

    print(f"running {args.tasks} tasks (seed={args.seed})...", file=sys.stderr)
    results = asyncio.run(_main_async(args))

    RESULTS_PATH.parent.mkdir(exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))

    s = results["strategies"]
    tail = results["config"]["tail"]
    print(f"\n{'strategy':<12} {'overall':>9} {f'last {tail}':>10} {'$/success':>11}")
    print("-" * 45)
    for name in STRATEGIES:
        r = s[name]
        print(
            f"{name:<12} {r['overall_accuracy']:>8.1%} {r['final_accuracy']:>10.1%} "
            f"{r['cost_per_success']:>11.4f}"
        )
    lift = s["horizon"]["final_accuracy"] - s["capability"]["final_accuracy"]
    print(f"\nfeedback-loop lift over capability-only: {lift:+.1%}")

    chk = results["sql_check"]
    print(
        f"sql check: {chk['linked_executions']} executions linked to a decision, "
        f"{chk['followed_share']:.0%} followed, "
        f"last {tail} accuracy from SQL {chk['final_accuracy_from_sql']:.1%}"
    )
    print(f"results written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
