# CLAUDE.md

Horizon provides memory infrastructure and memory-aware agent routing for AI
agent systems, as one API. Python 3.11+, FastAPI, async SQLAlchemy 2.0,
PostgreSQL 16 + pgvector.

This file holds **stable facts**: product decisions, architecture, conventions
and invariants. Things that change often live in `base/`.

## Where state lives

| File | Contents | Update when |
|---|---|---|
| `base/current-state.md` | What exists, what's verified, known gaps | A work session changes the state |
| `base/next-steps.md` | The next four steps, with done-criteria | A step is finished or reprioritized |
| `base/roadmap.md` | Phased roadmap with exit criteria | Evidence changes the plan |
| `base/pricing.md` | The published plan table and why | Pricing changes (mirror `PLAN_LIMITS`) |
| `base/metrics.md` | Traction + generated engineering/benchmark metrics | Traction changes; rest via `make metrics` |
| `README.md` | Public-facing docs, benchmark table | API or benchmark numbers change |
| `prd.md`, `.cursor/plans/*` | **Historical.** Superseded inputs, not specs | Never. Don't implement from them |

Where `prd.md` or the plans disagree with this file or the code, this file and the code win.

## Product decisions (made 2026-09-04, don't relitigate casually)

- **Goal:** a funded startup attempt. Traction is the deliverable, not just working software.
- **Scope:** one product. The memory core plus a thin routing layer. "Sapentia" as a
  separate product (from `prd.md`) is dropped; the name only survives in comments.
- **Wedge: routing memory.** The `executions` table records which agent succeeded at
  which task, so routing improves with volume. Plain AI memory is a commodity
  (Mem0, Zep, Letta) and exports cleanly. Routing history only has value inside the scorer.
- **Test for new work:** does it make the accuracy-over-time chart better, more
  believable, or seen by real users? That chart is the pitch.
- **Name: Horizon**, short form `hzn` (chosen 2026-09-20, replacing Antler, which
  collided with `antler.co`, a well-known VC firm and startup generator). `hzn` is
  the API key prefix (`hzn_live_`, `hzn_test_`) and the reserved package/handle.
  Still open: `horizon` is taken on PyPI (OpenStack Dashboard) and `horizon.com`
  is not available, so publish under `hzn` and settle the domain before launch.
- **Pricing: settled** — $0 / $29 / $249 / custom, metered on *routed decisions*,
  never on seats or stored memories. See `base/pricing.md` for the reasoning.

## Commands

```bash
make install   # uv venv (python 3.12) + editable install with dev extras
make db        # local pgserver Postgres at ~/.horizon/pgdata; prints DATABASE_URL
make migrate   # alembic upgrade head
make dev       # uvicorn on :8000, docs at /docs (needs OPENAI_API_KEY to embed)
make test      # pytest; starts its own Postgres in $TMPDIR/horizon-test-pgdata
make lint      # ruff check + ruff format --check
make typecheck # mypy horizon
make fmt       # ruff format + ruff check --fix
make check     # lint + typecheck + test
make bench     # 1000 tasks, seed 42 → benchmarks/results.json
make bench-repeat # 5 seeds → benchmarks/repeats.json (the honest spread)
make similarity   # similarity distributions → benchmarks/similarity.json
make chart     # → benchmarks/routing_benchmark.html
make metrics   # regenerate the generated half of base/metrics.md
```

No Docker or system Postgres is needed. `pgserver` ships Postgres 16 with pgvector.
`docker-compose.yml` is an optional alternative.

## Architecture

```
horizon/
  main.py            create_app(): CORS, routers, /health; lifespan refuses the
                     default API_KEY_PEPPER in production
  config/settings.py pydantic-settings, reads .env; get_settings() is lru_cached
  config/database.py async engine + SessionLocal created AT IMPORT; get_db() commits
                     on success, rolls back on error
  models/            Organization, APIKey, Memory, Agent, Execution, RoutingDecision
                     (UUID PKs, timestamps)
  schemas/           pydantic request/response models
  services/
    api_keys.py      hzn_live_/hzn_test_ keys, SHA-256(pepper:key), 16-char display prefix
    embeddings.py    EmbeddingProvider protocol; OpenAIEmbeddings (default),
                     DeterministicEmbeddings (offline hash BoW); get/set_embeddings()
    memory_service.py store (dedupe ≥0.95 in same org+collection), search (min 0.7)
    router.py        the routing engine (see below); save_decision() persists a
                     recommendation so the outcome can be linked back to it
  api/deps.py        get_current_org: Bearer or X-API-Key → hash lookup → Organization
  api/routes/        organizations.py, memories.py, agents.py (agents, route, executions)
  devdb.py           pgserver bootstrap for dev/tests/bench; nothing in the app imports it
migrations/          alembic, async env; hand-written revisions
                     (0001_initial_schema, 0002_routing_decisions)
benchmarks/          world.py (synthetic agents/tasks), run.py (simulation),
                     similarity.py (threshold calibration), chart.py
scripts/metrics.py   regenerates base/metrics.md from real artifacts
tests/               unit + integration against real Postgres
.github/workflows/   ci.yml — make install && make check, with HORIZON_REQUIRE_DB=1
```

**Request flow:** route handler → `CurrentOrg` dependency (API key auth) →
service function → async session → Postgres. All API paths sit under `/v1`.
Only `POST /v1/organizations` (signup) needs no auth.

### Routing engine (`horizon/services/router.py`)

For each enabled candidate agent in the org:

```
score = 0.6·evidence + 0.3·capability − 0.1·cost
```

- **capability**: cosine(task embedding, agent capability embedding), where the
  capability embedding comes from name + description + capabilities. Handles cold start.
- **evidence**: take up to 50 past executions in the org with similarity ≥ 0.75.
  Weight each by similarity × recency (30-day half-life). The outcome is
  `quality_score` if set, otherwise 1 for success and 0 for anything else.
  These build a `Beta(1+wins, 1+losses)` posterior, and ranking uses the
  **optimistic bound** `min(1, mean + 1.0·sd)`. An untried agent scores ≈ 0.79.
- **cost**: `cost_per_call_usd / max(cost)` across candidates. Only breaks ties.
- `exploring = True` when the greedy pick (posterior means) differs from the
  optimistic pick. `confidence` is 0.5·support saturation + 0.5·margin on means.

`POST /v1/route` writes a `routing_decisions` row and returns its `decision_id`.
`POST /v1/executions` takes that id and reads the task, its embedding and the
routing reason from that row — one embedding per task instead of two, an audit
trail the client cannot forge, and `followed` recording whether the caller
actually ran the recommended agent.

The docstrings and module header explain *why*. Keep them.

## Invariants: do not revert, remove, or "simplify"

1. **Evidence uses the optimistic bound, not the mean.** The first version used a
   weighted average, and the benchmark showed it picked the two best agents **0 of 1,000**
   times: the first adequate agent locks in and a better one is never tried. Any change
   to scoring must re-run `make bench` and must not drop Horizon's final-250 accuracy.
2. **Every query is org-scoped in SQL**, including single-row fetches by primary key
   (`_owned_memory`, `_owned_agent`). A guessed UUID must never cross tenants. Every new
   org-owned resource gets a cross-tenant test (see `test_*_never_crosses_tenants`).
3. **Agents are soft-disabled, never hard-deleted.** Deleting would take the execution
   history with it, and that history is the product.
4. **API keys are stored only as peppered SHA-256 hashes.** Plaintext is returned
   exactly once. SHA-256 rather than bcrypt is deliberate (256-bit random tokens; runs
   on every request). Changing `API_KEY_PEPPER` invalidates every key.
5. **UUID primary keys**, never serial. Sequential IDs leak tenant volume.
6. **HNSW indexes** (`m=16, ef_construction=64, vector_cosine_ops`), not IVFFlat. No
   training step, and recall holds under continuous inserts.
7. **Async all the way down.** No sync DB drivers or blocking calls in request paths.
8. **Benchmark honesty.** The headline comparison is Horizon vs **capability-only**
   (the same system without learning), never just vs random. Keep common random numbers
   (one shared uniform draw per task across strategies). Keep the "synthetic world,
   lexical embeddings" caveat wherever the numbers appear. The engine is **not**
   bit-reproducible — HNSW search is approximate, so the same seed varies by up to
   ~1pp on final-250. Quote the multi-seed spread from `make bench-repeat`, never a
   single run as if it were exact.
9. **A linked execution's `routing_reason` comes from the server**, copied from its
   `routing_decisions` row, never from the request body. The audit trail is worthless
   if the caller can write it. `followed` is NULL when unlinked — which is different
   from `false` ("the caller overrode us"); don't collapse the two.
10. **Pricing meters routed decisions**, never seats, stored memories, or reported
    executions. Reporting outcomes stays free forever: it is the one action that makes
    the product work.

## Conventions

**Code**
- ruff, line length 100, rules `E F I UP B ASYNC`. Target py311 (`StrEnum`, `X | None`).
- Comments and docstrings explain *why* (tradeoffs, failure modes, numbers), not what.
  Match that density in new code.
- Module-level constants with a comment explaining the chosen value (see `router.py`).

**Database / SQLAlchemy**
- Handlers and services call `flush()`, never `commit()`. `get_db` commits per request.
- **Build the pydantic response (`XOut.model_validate(obj)`) inside the handler** and
  return it. Never return ORM objects. A lazy load after the session closes raises
  `MissingGreenlet`.
- After flushing a row with server-side `onupdate` columns, `await db.refresh(obj)`
  before serializing (see `update_memory`).
- Bulk `update()` on already-loaded rows uses `.execution_options(synchronize_session=False)`
  (see `memory_service._touch`).
- The ORM attribute `Memory.meta` maps to the column `metadata` (a reserved name in
  SQLAlchemy). The API field is `metadata` via `validation_alias="meta"`.
- Schema changes go through a new hand-written alembic revision in `migrations/versions/`.
  Don't edit `0001`. Mirror the indexes declared next to the models.
- Embedding dimension is **1536**, hardcoded in migration `0001`. Changing
  `EMBEDDING_DIMENSIONS` needs a migration and re-embedding, not just an env change.

**Embeddings**
- Always go through `get_embeddings()`. Never construct `OpenAIEmbeddings` in routes.
- Tests and the benchmark call `set_embeddings(DeterministicEmbeddings())`. They
  must never make network calls.

**API**
- Versioned under `/v1`. Auth via `CurrentOrg`. Errors are `HTTPException` with a
  `detail` that tells the caller what to do.
- Missing or foreign resource → 404 (never 403, which would confirm the resource exists).
  Duplicate name/email → 409. No eligible agents → 422.

**Tests**
- Integration tests hit a real Postgres. The `db` fixture TRUNCATEs all tables per test.
- The pytest event loop is **session-scoped on purpose**: the engine is created at import
  and its asyncpg pool is bound to that loop. Don't switch to per-test loops.
- `conftest.py` sets `DATABASE_URL` *before* importing app modules. Keep that order.
- Name tests as sentences stating the behaviour (`test_a_proven_agent_is_not_displaced_by_an_unproven_one`).
- If no database can start, integration tests **skip**. In CI, check they ran.

**Git**
- **Conventional Commits**: `type(scope): imperative subject`, blank line, then a
  body explaining *why*. Types: `feat` `fix` `refactor` `perf` `docs` `test`
  `build` `ci` `chore`. Scopes: `routing` `memory` `api` `models` `db` `bench`
  `docs` `ci`. Breaking API or schema changes get a `BREAKING CHANGE:` footer.
- **One logical change per commit.** A rename, a migration, a pricing decision and
  a CI addition are four commits. Decide the boundaries before staging, not after.
  Commit `2addd9a` mixed all four; don't repeat it.
- Never add `Co-Authored-By` trailers and never mention any AI tool in a commit
  message, PR title or PR body.

**Safety**
- Tests and `make bench` TRUNCATE their databases (`$TMPDIR/horizon-test-pgdata`,
  `BENCH_PGDATA` or `/tmp/horizon-bench-pgdata`). Never point them at a real database.
- `.env` is gitignored and must stay that way. `.env.example` documents every variable.

## Environment variables

`ENVIRONMENT`, `DEBUG`, `DATABASE_URL` (a sync `postgresql://` URL is fine; it gets
rewritten to asyncpg), `DB_ECHO`, `OPENAI_API_KEY`, `EMBEDDING_MODEL`
(`text-embedding-3-small`), `EMBEDDING_DIMENSIONS` (1536), `API_KEY_PEPPER`
(required and non-default when `ENVIRONMENT=production`).
