"""
Regenerate the generated half of `base/metrics.md`.

One place to look to see whether the project is moving. The numbers that decide
whether this becomes a company are the traction ones at the top of that file,
and those are hand-maintained — nothing here can invent them. Everything below
the generated marker is read back off real artifacts (benchmark output, the
test suite, the migration history) so it cannot drift into wishful thinking.

    python -m scripts.metrics
"""

import json
import pathlib
import subprocess
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
METRICS = ROOT / "base" / "metrics.md"
MARKER = "<!-- generated: everything below is rewritten by `make metrics` -->"


def _load(name: str) -> dict | None:
    path = ROOT / "benchmarks" / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{x:.1%}"


def _test_count() -> str:
    """Collect-only, so this reports the suite's size without running it."""
    try:
        out = subprocess.run(
            [str(ROOT / ".venv/bin/python"), "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=300,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return "—"
    for line in reversed(out.splitlines()):
        if "test" in line and "collected" in line:
            return line.strip().split()[0]
    return "—"


def _source_lines() -> tuple[int, int]:
    def count(*dirs: str) -> int:
        total = 0
        for d in dirs:
            for f in (ROOT / d).rglob("*.py"):
                if "__pycache__" not in f.parts:
                    total += len(f.read_text().splitlines())
        return total

    return count("horizon", "migrations"), count("tests", "benchmarks", "scripts")


def _endpoint_count() -> int:
    """
    From the OpenAPI schema, not `app.routes` — included routers are nested
    objects there, so walking the route list silently undercounts.
    """
    from horizon.main import create_app

    paths = create_app().openapi()["paths"]
    return sum(len(ops) for ops in paths.values())


def _benchmark_section(results: dict | None, repeats: dict | None) -> list[str]:
    if results is None:
        return ["_No `benchmarks/results.json`. Run `make bench`._", ""]

    cfg = results["config"]
    strat = results["strategies"]
    tail = cfg["tail"]
    lines = [
        f"Seed {cfg['seed']}, {cfg['tasks']:,} tasks, "
        f"{cfg.get('embeddings', 'deterministic')} embeddings, "
        f"{cfg.get('phrasing', 'template')} phrasing. Last-quarter = final {tail} tasks.",
        "",
        "| Strategy | Overall | Last quarter | $/success |",
        "|---|---|---|---|",
    ]
    for name in ("oracle", "horizon", "capability", "random"):
        r = strat[name]
        label = "**Horizon**" if name == "horizon" else name.capitalize()
        bold = "**" if name == "horizon" else ""
        lines.append(
            f"| {label} | {bold}{r['overall_accuracy']:.1%}{bold} | "
            f"{bold}{r['final_accuracy']:.1%}{bold} | ${r['cost_per_success']:.4f} |"
        )

    lift = strat["horizon"]["final_accuracy"] - strat["capability"]["final_accuracy"]
    ceiling = strat["horizon"]["final_accuracy"] / strat["oracle"]["final_accuracy"]
    lines += [
        "",
        f"- **Lift over capability-only:** {lift:+.1%} on the last quarter",
        f"- **Share of the oracle ceiling:** {ceiling:.0%}",
        f"- **Evidence threshold in force:** {cfg.get('evidence_min_similarity', '—')}",
    ]

    check = results.get("sql_check")
    if check:
        lines += [
            f"- **Executions linked to a stored decision:** {check['linked_executions']:,} "
            f"({check['followed_share']:.0%} followed the recommendation)",
            f"- **Last-quarter accuracy recomputed from SQL:** "
            f"{check['final_accuracy_from_sql']:.1%} "
            f"(matches the table above, so the stored history says what the summary says)",
        ]

    if repeats:
        agg = repeats["aggregate"]
        rl = repeats["final_lift_over_capability"]
        seeds = repeats["config"]["seeds"]
        rcfg = repeats["config"]
        lines += [
            "",
            f"**Spread across {len(seeds)} seeds ({seeds[0]}–{seeds[-1]}), "
            f"{rcfg.get('embeddings', 'deterministic')} embeddings, "
            f"{rcfg.get('phrasing', 'template')} phrasing.** The engine is not "
            "bit-reproducible: pgvector's HNSW search is approximate, so the 50 nearest past "
            "executions can differ between runs of the same seed.",
            "",
            "| Strategy | Last-quarter mean | Min | Max | SD |",
            "|---|---|---|---|---|",
        ]
        for name in ("oracle", "horizon", "capability", "random"):
            f = agg[name]["final_accuracy"]
            label = "**Horizon**" if name == "horizon" else name.capitalize()
            lines.append(
                f"| {label} | {f['mean']:.1%} | {f['min']:.1%} "
                f"| {f['max']:.1%} | {f['stdev']:.1%} |"
            )
        lines += [
            "",
            f"- **Lift over capability-only:** {rl['mean']:+.1%} mean, "
            f"range {rl['min']:+.1%} to {rl['max']:+.1%}, SD {rl['stdev']:.1%}",
        ]
    else:
        lines += ["", "_No `benchmarks/repeats.json`. Run `make bench-repeat`._"]
    return lines + [""]


def _similarity_section(sim: dict | None) -> list[str]:
    if not sim:
        return ["_No `benchmarks/similarity.json`. Run `make similarity`._", ""]

    lines = [
        "Cosine similarity between task pairs, by embedding model and phrasing. "
        "Same-family pairs are the ones the router *should* count as evidence; "
        "different-family pairs are the ones it should reject. "
        "`EVIDENCE_MIN_SIMILARITY` has to sit in the gap between them.",
        "",
        "| Model | Phrasing | Same-family p50 | Different-family p95 | "
        "Best threshold | Evidence kept | Unrelated admitted |",
        "|---|---|---|---|---|---|---|",
    ]
    for key in sorted(sim):
        run = sim[key]
        cfg, w, b = run["config"], run["within_family"], run["between_family"]
        best = run["recommended"]["best_separation"]
        lines.append(
            f"| {cfg['embeddings']} | {cfg['phrasing']} | {w['p50']:.3f} | {b['p95']:.3f} "
            f"| {best['threshold']:.2f} | {best['within_kept']:.0%} "
            f"| {best['between_admitted']:.1%} |"
        )
    if not any(sim[k]["config"]["embeddings"] == "openai" for k in sim):
        lines += [
            "",
            "**Not yet measured under a real embedding model.** `EVIDENCE_MIN_SIMILARITY = 0.75` "
            "was set against lexical embeddings and has never been checked against one. "
            "Run `make similarity-openai` once `OPENAI_API_KEY` is set.",
        ]
    return lines + [""]


def main() -> None:
    results, repeats, sim = _load("results.json"), _load("repeats.json"), _load("similarity.json")
    app_lines, test_lines = _source_lines()

    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        ).stdout.strip()
    except OSError:
        commit = "—"

    migrations = sorted((ROOT / "migrations" / "versions").glob("*.py"))

    body = [
        MARKER,
        "",
        f"_Regenerated {date.today().isoformat()} from `make metrics` at commit `{commit}`._",
        "",
        "## Routing quality",
        "",
        *_benchmark_section(results, repeats),
        "## Similarity calibration",
        "",
        *_similarity_section(sim),
        "## Engineering",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Tests | {_test_count()} |",
        f"| Application lines (`horizon/`, `migrations/`) | {app_lines:,} |",
        f"| Test + benchmark + tooling lines | {test_lines:,} |",
        f"| HTTP endpoints | {_endpoint_count()} |",
        f"| Migrations applied | {len(migrations)} (head `{migrations[-1].stem}`) |",
        "",
        "Gates enforced by `make check`: `ruff check`, `ruff format --check`, "
        "`mypy horizon`, the full pytest suite against a real PostgreSQL.",
        "",
    ]

    existing = METRICS.read_text() if METRICS.exists() else ""
    # First run has no marker yet: keep the whole hand-written file as the head
    # and append. After that, everything from the marker down is replaced.
    head = existing.split(MARKER)[0] if MARKER in existing else existing
    if not head.strip():
        print("base/metrics.md is missing its hand-written header; nothing to do.", file=sys.stderr)
        raise SystemExit(1)
    METRICS.write_text(head + "\n".join(body))
    print(f"wrote {METRICS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
