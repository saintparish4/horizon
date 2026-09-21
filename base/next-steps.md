# Next steps

Rewritten **2026-09-20**, after the session that renamed the project, settled
pricing, and landed the previous steps 1-3. Every step is judged by one
question: *does this make the accuracy-over-time chart better or more
believable, or get it in front of real users?* That chart is the pitch.

Do them in order. Start step 3 now, alongside 1 and 2, because conversations
take longer than code.

---

## 1. Recalibrate the evidence threshold against a real embedding model

**Why first:** it is the cheapest thing on this list and the first question a
technical investor or user will ask. `make similarity` now measures the two
distributions the threshold has to separate, and the answer under the
benchmark's lexical embeddings is unambiguous:

| Model | Phrasing | Same-family p50 | Different-family p95 | Evidence kept at 0.75 |
|---|---|---|---|---|
| deterministic | template | 0.833 | 0.199 | 92% |
| deterministic | paraphrase | 0.261 | 0.250 | 24% |

Slot-filled tasks separate perfectly, so the benchmark's 0.75 works. Paraphrase
the same tasks and same-family similarity collapses into the unrelated
distribution — the threshold discards three-quarters of the real evidence and
the router quietly degrades to capability-only. Real models put short related
strings far higher and in a much narrower band, so 0.75 is very likely wrong for
production in one direction or the other.

Everything needed is built. What is missing is the key.

- Set `OPENAI_API_KEY` in `.env` (the only blocker; costs a few cents).
- `make similarity-openai` — writes both phrasings into `benchmarks/similarity.json`.
- Pick `EVIDENCE_MIN_SIMILARITY` from that data and update the comment above the
  constant in `horizon/services/router.py`, which already records how the
  current value was derived.
- `python -m benchmarks.run --embeddings openai --phrasing paraphrase` to confirm
  the lift survives under both the real model and paraphrased tasks.
- Publish both results in the README, keeping the "synthetic world" caveat.

**Done when:** the README shows real-model results, and the threshold in the
code comes with the similarity-distribution data behind it.

## 2. Ship a hostable alpha

**Why:** the goal is a funded company, and traction is the deliverable. The
benchmark shows the mechanism works; only outside teams sending real executions
show it matters.

Minimum needed to expose it safely:

- Rate limiting on `POST /v1/organizations` and per API key. Signup is open, and
  every write spends embedding budget.
- `DELETE /v1/api-keys/{id}` to revoke a key (sets `revoked_at`, which auth
  already checks) and `GET /v1/api-keys` to list them. The docstring on
  `POST /v1/api-keys` promises revocation that does not exist.
- A `Dockerfile`, then deploy (Railway/Render/Fly + Neon or Supabase Postgres
  with pgvector). Production needs a real `API_KEY_PEPPER`; startup already
  refuses the default.
- A thin Python SDK (`httpx`) built around the loop:
  `decision = client.route(task)` → caller runs the agent →
  `client.report(decision, status, quality=...)`. Publish as `hzn`.
- A one-page quickstart covering signup → register agents → route → report.

**Done when:** someone outside this repo can sign up, route, and report without
reading the source.

## 3. Get 3-5 design partners reporting executions weekly

**Why:** every number in `base/metrics.md` above the generated marker is a zero.
They are the only numbers that decide whether this becomes a company.

- Target teams that already run more than one agent and already have a routing
  problem: agent-framework users (LangGraph, CrewAI), internal platform teams,
  anyone running a model router today.
- The pitch is the chart plus the honest caveat: "this is synthetic; be the
  first real workload on it."
- Instrument the ask — the free tier at 10,000 routed decisions/month is sized
  to be enough for a real pilot without a card.

**Done when:** at least three outside teams report executions every week, and
`base/metrics.md`'s traction table has non-zero rows.

## 4. Show lift on real traffic

**Why:** the synthetic benchmark shows the mechanism works. This shows the
effect on real work, which is the seed-round artifact.

- **Holdout policy:** route a small, configurable share of each org's traffic
  capability-only, flagged on the `routing_decisions` row. That is a real
  control group — the same comparison as the benchmark, on customer data.
- **Per-org metrics endpoint:** success rate over time, Horizon vs holdout,
  exploration rate, per-agent success by task cluster. `followed` already
  distinguishes a followed recommendation from an override.
- **Late feedback:** `PATCH /v1/executions/{id}` to set `quality_score` and
  `feedback_at`. Real quality signals often arrive after the call returns, and
  `feedback_at` exists on the model with nothing to write it.

**Done when:** a chart built from design-partner data shows Horizon beating the
holdout, with enough executions behind it that the gap is not noise.

---

After these four, see `base/roadmap.md`, Phase 3 onward.
