# Horizon

**Memory infrastructure and memory-aware routing for AI agent systems.** `hzn` for short.

Horizon is two things behind one API:

1. **Memory** — store, embed, and semantically search persistent context, scoped per tenant, per collection, per user, per session.
2. **Routing** — decide which registered agent should handle a task, based on what actually worked for semantically similar tasks before.

The second part is the point. A vector store with an API key is a commodity;
a router that gets measurably better as it accumulates execution history is not.

## Status

Pre-alpha. The API below is implemented, typechecked and tested against a real
PostgreSQL. There is no SDK, dashboard, or hosted deployment yet, and no
outside users. Progress is tracked in [`base/metrics.md`](base/metrics.md).

## Quickstart

```bash
make install          # uv venv + editable install
make db               # local postgres 16 + pgvector — prints a DATABASE_URL
cp .env.example .env  # paste that URL, set OPENAI_API_KEY and API_KEY_PEPPER
make migrate          # create schema
make dev              # http://localhost:8000/docs
```

`make db` needs neither Docker nor a system Postgres — `pgserver` ships a
self-contained PostgreSQL 16 build with pgvector. For a hosted database instead,
point `DATABASE_URL` at any Postgres 16+ with the `vector` extension available
(Neon and Supabase both ship it) and run `make migrate`. A `docker-compose.yml`
is included if you prefer that route.

## The loop

```
POST /v1/route        →  { decision_id, selected_agent, confidence, reason }
        ↓  you run the agent
POST /v1/executions   →  { decision_id, agent_id, status, quality_score? }
        ↓
   the next /v1/route is better
```

Routing only improves if callers close that loop. Without outcomes the router
degrades gracefully to capability similarity — which is exactly the
`capability-only` baseline the benchmark below measures against.

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/organizations` | Sign up, receive first API key (open endpoint) |
| `GET` | `/v1/organizations/me` | Plan, limits, and usage counts |
| `POST` | `/v1/api-keys` | Issue an additional key |
| `POST` | `/v1/memories` | Store a memory (embeds, optionally dedupes) |
| `POST` | `/v1/memories/search` | Semantic search with filters |
| `GET` | `/v1/memories` | List with filters + pagination |
| `GET/PATCH/DELETE` | `/v1/memories/{id}` | Read, update (re-embeds), delete |
| `POST` | `/v1/agents` | Register an agent |
| `GET` | `/v1/agents` | List agents |
| `DELETE` | `/v1/agents/{id}` | Disable (soft — preserves history) |
| `POST` | `/v1/route` | Pick the best agent; records the decision |
| `POST` | `/v1/executions` | Report an outcome — this is the learning loop |
| `GET` | `/v1/executions` | Execution history |

Auth is `Authorization: Bearer <key>` or `X-API-Key: <key>` on everything
except signup. Keys look like `hzn_live_…`.

## How routing works

For a task, each enabled agent is scored:

```
score = 0.6 * evidence + 0.3 * capability - 0.1 * cost
```

- **evidence** — an *optimistic* estimate of how well this agent handles tasks
  like this one, from a Beta posterior over semantically similar past
  executions, weighted by task similarity and recency (30-day half-life, so
  stale wins fade as agents and models get swapped out).
- **capability** — cosine similarity between the task and the agent's declared
  capabilities. This carries routing at cold start, before history exists.
- **cost** — declared cost per call, normalized across candidates. Tie-breaker only.

### Why evidence is optimistic, not an average

This is a contextual bandit, and ranking on the observed mean is
self-reinforcing: an agent only accrues history for tasks it already wins, so
the first adequate agent locks in and a better one is never tried. With a
mediocre incumbent at 0.52 and `w_evidence = 0.6`, an untried agent would need a
capability advantage above 1.0 to displace it — impossible, since cosine
similarity is bounded at 1.

So each agent carries a `Beta(1 + wins, 1 + losses)` posterior over similar
tasks and is scored at `mean + 1.0 * sd`. An untried agent sits near 0.79 and
outranks a known-mediocre one; as evidence accumulates the interval narrows onto
the true rate and exploration stops on its own.

This was not a hypothetical. The first version of this router used a plain
weighted average, and the benchmark below showed it selecting the two best
agents **zero times out of 1,000**.

### The decision payload

Every decision returns a `decision_id` and a `reason` naming each agent
considered with its component scores — including `evidence` (the optimistic
bound), `evidence_mean` (what was actually observed) and `evidence_sd` (how
unsure) — plus:

- `confidence` — the exploitation view: how much evidence backs the winner and
  how clearly it leads on posterior means.
- `exploring` — true when the optimism bonus produced the pick, i.e. a different
  agent would have won on means alone. Callers that can't gamble on a given
  request can check this and override.

The decision is **stored server-side** before you act on it. Pass its
`decision_id` back to `POST /v1/executions` and three things follow: the task is
embedded once per task rather than twice, the audit trail is the server's own
record rather than something the client echoes back, and `followed` records
whether you actually ran the agent we recommended — which is what separates
"the router was wrong" from "the router was overruled" once real traffic
arrives.

## Benchmark

`benchmarks/` simulates 1,000 tasks across four task families and five agents
whose true competence is hidden from the router — and who over-claim in their
declared capabilities, as real agent registries do.

```bash
make bench         # one seed → benchmarks/results.json
make bench-repeat  # five seeds → benchmarks/repeats.json
make chart         # renders benchmarks/routing_benchmark.html
```

**Accuracy over the final quarter of the run, across 5 seeds:**

| Strategy | Mean | Min | Max |
|---|---|---|---|
| Oracle ceiling | 92.0% | 90.4% | 94.0% |
| **Horizon** | **90.9%** | 86.8% | 93.6% |
| Capability-only | 71.0% | 67.6% | 76.0% |
| Random | 41.4% | 36.8% | 45.6% |

Horizon reaches **99% of the achievable ceiling**, a **+19.9pp** mean lift over
the identical router with the feedback loop switched off (range +17.6 to +22.8,
SD 2.5). Capability-only never selects the two genuinely-best specialists even
once; the generalist that over-claims every family wins on declared capability
and is never challenged.

Methodology notes, because they determine whether the numbers mean anything:

- **Capability-only is the honest comparison.** It is the same system minus the
  learning, so the gap isolates what execution history contributes. Comparing
  against `random` alone would flatter the result.
- **Common random numbers.** Every strategy sees the same task stream and the
  same uniform draw per task, which makes the comparison paired and makes the
  oracle a strict per-task upper bound. With independent draws a strategy can
  beat its own oracle on sampling luck — which the first version of this
  benchmark did.
- **Five seeds, not one.** The engine is not bit-reproducible: pgvector's HNSW
  search is approximate, so the 50 nearest past executions can differ between
  runs of *the same* seed. Single-seed runs of this benchmark land anywhere from
  86.8% to 93.6%. Quoting the best one would be cherry-picking.
- **Offline deterministic embeddings**, so runs are reproducible and cost
  nothing. These capture lexical overlap, not semantics; they exercise the real
  pgvector/HNSW/SQL path but they are not a substitute for measuring against a
  real embedding model on real tasks.
- **Every execution is linked to its stored decision** and 100% of them followed
  the recommendation, so the accuracy above can be — and is — recomputed
  directly from SQL over `executions ⋈ routing_decisions`.

This is a synthetic world, calibrated by hand. It demonstrates that the
mechanism works and quantifies the gap under stated assumptions; it is not
evidence about any real workload.

### The known weak spot

`make similarity` measures the two distributions the evidence threshold has to
separate — similarity between same-family task pairs (should count as evidence)
and between different-family pairs (should not):

| Model | Phrasing | Same-family p50 | Different-family p95 | Evidence kept at 0.75 |
|---|---|---|---|---|
| deterministic | template | 0.833 | 0.199 | 92% |
| deterministic | paraphrase | 0.261 | 0.250 | 24% |
| **real model** | — | **not yet measured** | | |

The first row is why the benchmark works. The second is the warning: once tasks
are paraphrased rather than slot-filled, lexical similarity stops distinguishing
related work from unrelated work at all, and the threshold throws away
three-quarters of the genuine evidence. Real embedding models score short
related strings much higher and in a far narrower band, so `0.75` is very
unlikely to be right for production traffic. Recalibrating it against a real
model is [next-steps](base/next-steps.md) item 1 and needs nothing but an
`OPENAI_API_KEY`.

## Pricing

Metered on **routed decisions** — never on seats, stored memories, or reported
outcomes. Reporting outcomes is free forever: it is the one action that makes
the product work.

| | Free | Starter | Pro | Enterprise |
|---|---|---|---|---|
| Monthly | $0 | $29 | $249 | custom |
| Routed decisions | 10,000 | 100,000 | 1,500,000 | custom |
| Overage / 1,000 | — | $0.50 | $0.30 | custom |
| Stored memories | 50,000 | 500,000 | 5,000,000 | custom |
| History retained | 30 days | 90 days | 13 months | unlimited |
| Seats | unlimited | unlimited | unlimited | unlimited |

Nothing is metered or billed yet — this is the published shape, not a running
billing system. Reasoning and comparables in [`base/pricing.md`](base/pricing.md).

## Design decisions

- **Async throughout.** SQLAlchemy 2.0 async + asyncpg. Routing does a vector
  search per request; blocking the event loop on it does not scale.
- **UUID primary keys.** Sequential integers leak tenant volume across a
  multi-tenant boundary.
- **API keys are hashed, never stored.** SHA-256 over a server-side pepper.
  Plaintext is returned once at creation. SHA-256 rather than bcrypt is
  deliberate: these are 256-bit random tokens, not user-chosen passwords, so
  there is no dictionary to attack and verification runs on every request.
- **HNSW, not IVFFlat.** No training step, and recall holds up under the
  continuous inserts that define a memory store's write pattern.
- **Every query is org-scoped at the SQL level**, including single-row fetches
  by primary key, so a guessed UUID cannot cross tenants.
- **Soft-disable agents.** Hard deletion would take the execution history with
  it, and that history is the thing that makes routing worth paying for.
- **The routing reason comes from the server.** On a linked execution it is
  copied from the stored decision, never from the request body. An audit trail
  the caller can write is not an audit trail.

## Layout

```
horizon/
  config/      settings (pydantic-settings), async engine + session
  models/      Organization, APIKey, Memory, Agent, Execution, RoutingDecision
  schemas/     pydantic request/response models
  services/    embeddings, api keys, memory ops, routing engine
  api/         deps (auth) + routes
  devdb.py     self-contained local postgres for dev and tests
migrations/    alembic (0001 schema, 0002 routing decisions)
benchmarks/    synthetic world, simulation runner, similarity calibration, HTML report
scripts/       metrics.py — regenerates base/metrics.md from real artifacts
tests/         unit plus integration against a live database
base/          current state, next steps, roadmap, pricing, metrics
```

## Development

```bash
make test       # spins up a throwaway postgres automatically
make lint       # ruff check + format check
make typecheck  # mypy
make check      # all three
make metrics    # refresh base/metrics.md
```

Integration tests run against a real PostgreSQL with pgvector and swap in
offline embeddings, so the full SQL / vector-search / HNSW path is exercised
without a network call. They skip cleanly if no database can be started — and
CI sets `HORIZON_REQUIRE_DB=1` to turn that skip into a hard failure, because a
green run that tested nothing looks exactly like a real one.

## Roadmap

Near term (see [`base/next-steps.md`](base/next-steps.md)):
- Recalibrate the evidence threshold against a real embedding model
- Key revocation, signup rate limiting, a Dockerfile, a hosted deployment
- A thin Python SDK around `route → run → report`
- Usage metering and plan enforcement (limits exist; nothing enforces them)
- Agent invocation — Horizon currently *recommends* an agent; it does not call it

Later: TypeScript SDK, dashboard, MCP protocol support, memory decay/pruning.
Full phasing in [`base/roadmap.md`](base/roadmap.md).

## Naming

Renamed from **Antler** on 2026-09-20: `antler.co` is an established global VC
and startup generator, and this sells into the startup ecosystem — a collision
worth resolving before a package, domain or launch post existed rather than
after.

`Horizon` is not unclaimed either. `horizon` is taken on PyPI (OpenStack
Dashboard) and `horizon.com` is unavailable, so the short form **`hzn`** is the
publishing handle: `hzn_live_` API keys, `hzn` on PyPI and npm. The domain is
still unsettled and should be before anything is published.
