"""
Where should EVIDENCE_MIN_SIMILARITY sit?

The router counts a past execution as evidence when its task is at least
`EVIDENCE_MIN_SIMILARITY` similar to the new one. That threshold was originally
guessed at 0.75 against hashed bag-of-words embeddings. Different embedding
models put their similarity scores in entirely different ranges — a real model
rarely scores unrelated short strings below 0.6 — so a threshold carried over
unexamined either admits every past task as evidence (the router learns one
global prior and stops being contextual) or admits none (it degrades to
capability-only, silently).

This measures the two distributions that actually matter:

  within   pairs of tasks from the same family — these SHOULD count as evidence
  between  pairs from different families — these should NOT

and reports the threshold that best separates them, so the constant is a
measurement rather than a guess.

    python -m benchmarks.similarity
    python -m benchmarks.similarity --embeddings openai --phrasing paraphrase
"""

import argparse
import asyncio
import itertools
import json
import math
import pathlib
import random
import statistics

RESULTS_PATH = pathlib.Path("benchmarks/similarity.json")

# Candidate thresholds to score. Finer than anyone would hand-tune.
GRID = [round(0.40 + 0.01 * i, 2) for i in range(61)]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _percentiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)

    def pct(p: float) -> float:
        if not ordered:
            return 0.0
        idx = min(len(ordered) - 1, max(0, int(round(p / 100 * (len(ordered) - 1)))))
        return ordered[idx]

    return {
        "n": len(ordered),
        "p01": pct(1),
        "p05": pct(5),
        "p25": pct(25),
        "p50": pct(50),
        "p75": pct(75),
        "p95": pct(95),
        "p99": pct(99),
        "mean": statistics.mean(ordered) if ordered else 0.0,
    }


async def measure(per_family: int, seed: int, embeddings: str, paraphrase: bool) -> dict:
    from benchmarks.run import _provider
    from benchmarks.world import FAMILIES

    provider = _provider(embeddings)
    rng = random.Random(seed)

    tasks: dict[str, list[str]] = {
        f.name: [f.render(rng, paraphrase=paraphrase) for _ in range(per_family)] for f in FAMILIES
    }
    vectors: dict[str, list[list[float]]] = {}
    for name, texts in tasks.items():
        vectors[name] = await provider.embed(texts)

    within: list[float] = []
    between: list[float] = []
    within_by_family: dict[str, list[float]] = {}

    for name, vecs in vectors.items():
        sims = [_cosine(a, b) for a, b in itertools.combinations(vecs, 2)]
        within_by_family[name] = sims
        within.extend(sims)

    for a_name, b_name in itertools.combinations(vectors, 2):
        for va in vectors[a_name]:
            for vb in vectors[b_name]:
                between.append(_cosine(va, vb))

    # Youden's J: the threshold that maximises (kept evidence) - (false evidence).
    # A threshold is only useful if it keeps same-family history while rejecting
    # unrelated history; J scores exactly that trade-off, with no free parameter.
    scored = []
    for t in GRID:
        recall = sum(1 for s in within if s >= t) / len(within) if within else 0.0
        leak = sum(1 for s in between if s >= t) / len(between) if between else 0.0
        scored.append(
            {
                "threshold": t,
                "within_kept": recall,
                "between_admitted": leak,
                "youden_j": recall - leak,
            }
        )
    best = max(scored, key=lambda r: r["youden_j"])

    # A stricter, more conservative option: the tightest threshold that lets in
    # under 1% of unrelated history, even at the cost of some real evidence.
    clean = [r for r in scored if r["between_admitted"] <= 0.01]
    conservative = min(clean, key=lambda r: r["threshold"]) if clean else None

    return {
        "config": {
            "per_family": per_family,
            "seed": seed,
            "embeddings": embeddings,
            "phrasing": "paraphrase" if paraphrase else "template",
        },
        "within_family": _percentiles(within),
        "between_family": _percentiles(between),
        "within_by_family": {k: _percentiles(v) for k, v in within_by_family.items()},
        "recommended": {
            "best_separation": best,
            "conservative_1pct_leak": conservative,
        },
        "grid": scored,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-family", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--embeddings", choices=("deterministic", "openai"), default="deterministic"
    )
    parser.add_argument("--phrasing", choices=("template", "paraphrase"), default="template")
    args = parser.parse_args()

    result = asyncio.run(
        measure(args.per_family, args.seed, args.embeddings, args.phrasing == "paraphrase")
    )
    # Accumulate rather than overwrite: the whole point is the comparison
    # between models and phrasings, and each run measures exactly one cell.
    RESULTS_PATH.parent.mkdir(exist_ok=True)
    everything = {}
    if RESULTS_PATH.exists():
        try:
            everything = json.loads(RESULTS_PATH.read_text())
        except json.JSONDecodeError:
            everything = {}
    everything[f"{args.embeddings}-{args.phrasing}"] = result
    RESULTS_PATH.write_text(json.dumps(everything, indent=2))

    cfg = result["config"]
    print(f"\n{cfg['embeddings']} embeddings, {cfg['phrasing']} phrasing")
    print(f"{'':<16}{'p05':>8}{'p25':>8}{'p50':>8}{'p75':>8}{'p95':>8}{'pairs':>9}")
    print("-" * 65)
    for label, key in (("within family", "within_family"), ("between family", "between_family")):
        d = result[key]
        print(
            f"{label:<16}{d['p05']:>8.3f}{d['p25']:>8.3f}{d['p50']:>8.3f}"
            f"{d['p75']:>8.3f}{d['p95']:>8.3f}{d['n']:>9,}"
        )

    best = result["recommended"]["best_separation"]
    print(
        f"\nbest separation at {best['threshold']:.2f}: "
        f"keeps {best['within_kept']:.0%} of same-family evidence, "
        f"admits {best['between_admitted']:.1%} of unrelated (J={best['youden_j']:.3f})"
    )
    cons = result["recommended"]["conservative_1pct_leak"]
    if cons:
        print(
            f"under 1% leak from {cons['threshold']:.2f}: "
            f"keeps {cons['within_kept']:.0%} of same-family evidence"
        )
    else:
        print("no threshold on the grid holds unrelated evidence under 1%")
    print(f"\nwritten to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
