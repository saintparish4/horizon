# Metrics

The one page to check whether this is working. Two halves:

- **Traction** is hand-maintained. Nothing can generate it, and it is the half
  that decides whether Horizon becomes a company. Update it when it changes.
- Everything under the generated marker is rewritten by `make metrics`, read
  back off real artifacts — the benchmark output, the test suite, the migration
  history — so it cannot drift into wishful thinking.

## Traction — update by hand

Snapshot **2026-09-20**.

| Metric | Value | Target for the seed story |
|---|---|---|
| Design partners sending executions | 0 | 3–5 |
| Orgs signed up on a hosted instance | 0 | 20 |
| Routed decisions on real traffic | 0 | 100,000 |
| Executions reported on real traffic | 0 | 50,000 |
| Orgs reporting executions weekly | 0 | 3 |
| Paying customers | 0 | 1 |
| MRR | $0 | — |

Nothing is deployed yet, so every number above is a true zero rather than an
unmeasured one. The first non-zero row is the point of `base/next-steps.md`
step 4.

**How to fill these in once there is a hosted instance:** `GET
/v1/organizations/me` already returns `routed_decisions_this_month`,
`executions_recorded` and `executions_with_feedback` per org; the weekly-active
count is a query over `routing_decisions` grouped by `org_id`.

<!-- generated: everything below is rewritten by `make metrics` -->

_Regenerated 2026-09-20 from `make metrics` at commit `cd5e6fa`._

## Routing quality

Seed 42, 1,000 tasks, deterministic embeddings, template phrasing. Last-quarter = final 250 tasks.

| Strategy | Overall | Last quarter | $/success |
|---|---|---|---|
| Oracle | 90.1% | 91.6% | $0.0117 |
| **Horizon** | **88.6%** | **90.8%** | $0.0116 |
| Capability | 71.1% | 68.8% | $0.0109 |
| Random | 42.4% | 36.8% | $0.0229 |

- **Lift over capability-only:** +22.0% on the last quarter
- **Share of the oracle ceiling:** 99%
- **Evidence threshold in force:** 0.75
- **Executions linked to a stored decision:** 1,000 (100% followed the recommendation)
- **Last-quarter accuracy recomputed from SQL:** 90.8% (matches the table above, so the stored history says what the summary says)

**Spread across 5 seeds (42–46), deterministic embeddings, template phrasing.** The engine is not bit-reproducible: pgvector's HNSW search is approximate, so the 50 nearest past executions can differ between runs of the same seed.

| Strategy | Last-quarter mean | Min | Max | SD |
|---|---|---|---|---|
| Oracle | 92.0% | 90.4% | 94.0% | 1.7% |
| **Horizon** | 90.9% | 86.8% | 93.6% | 2.8% |
| Capability | 71.0% | 67.6% | 76.0% | 4.1% |
| Random | 41.4% | 36.8% | 45.6% | 3.4% |

- **Lift over capability-only:** +19.9% mean, range +17.6% to +22.8%, SD 2.5%

## Similarity calibration

Cosine similarity between task pairs, by embedding model and phrasing. Same-family pairs are the ones the router *should* count as evidence; different-family pairs are the ones it should reject. `EVIDENCE_MIN_SIMILARITY` has to sit in the gap between them.

| Model | Phrasing | Same-family p50 | Different-family p95 | Best threshold | Evidence kept | Unrelated admitted |
|---|---|---|---|---|---|---|
| deterministic | paraphrase | 0.261 | 0.250 | 0.41 | 31% | 0.0% |
| deterministic | template | 0.833 | 0.199 | 0.40 | 100% | 0.0% |

**Not yet measured under a real embedding model.** `EVIDENCE_MIN_SIMILARITY = 0.75` was set against lexical embeddings and has never been checked against one. Run `make similarity-openai` once `OPENAI_API_KEY` is set.

## Engineering

| Metric | Value |
|---|---|
| Tests | 75 |
| Application lines (`horizon/`, `migrations/`) | 2,306 |
| Test + benchmark + tooling lines | 2,645 |
| HTTP endpoints | 16 |
| Migrations applied | 2 (head `0002_routing_decisions`) |

Gates enforced by `make check`: `ruff check`, `ruff format --check`, `mypy horizon`, the full pytest suite against a real PostgreSQL.
