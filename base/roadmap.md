# Roadmap

Proposed 2026-09-16, revised **2026-09-20**. Phases are ordered by what the
fundraise needs, not by feature count. Each phase has an exit criterion, and a phase isn't done until
that criterion is met. Update this file once design partners start producing evidence.

The thesis every phase serves: **routing gets measurably better as execution
history builds up, and that history only has value inside Horizon's scorer.**
Plain AI memory is a commodity (Mem0, Zep, Letta) and exports cleanly. Routing
history doesn't.

---

## Phase 1: Foundation and alpha

*This is `base/next-steps.md` steps 1-3.*

- ~~Rebuild committed, CI green, mypy in `make check`~~ — done 2026-09-20
- ~~Routing decisions saved and linked to executions (`decision_id`)~~ — done 2026-09-20
- ~~Name settled before anything is published~~ — Horizon / `hzn`, 2026-09-20
- ~~Pricing settled~~ — $0/$29/$249/custom on routed decisions, 2026-09-20
- Benchmark run against a real embedding model, thresholds recalibrated
  *(tooling built; blocked only on `OPENAI_API_KEY`)*
- Hosted deployment, signup/key rate limits, key revocation
- Thin Python SDK plus quickstart

**Exit:** 3-5 design partners report executions every week.

## Phase 2: Show lift on real traffic

The synthetic benchmark shows the mechanism works. This phase shows the
effect on real work, which is the seed-round artifact.

- **Holdout policy:** send a small, configurable share of each org's traffic
  through capability-only routing, flagged on the decision record. That gives
  a real control group, the same comparison as the benchmark but on customer data.
  The `routing_decisions` table and the `followed` flag, both landed 2026-09-20,
  are the substrate this needs.
- **Per-org metrics endpoint:** success rate over time, Horizon vs holdout,
  exploration rate, per-agent success by task cluster.
- **Late feedback:** `PATCH /v1/executions/{id}` sets `quality_score` and
  `feedback_at`. Real quality signals often arrive after the call returns.
- Fallback info on the decision: the ranked runner-up, so callers can retry
  with the next-best agent.

**Exit:** a chart built from design-partner data that shows Horizon beating the
holdout, with enough executions behind it that the gap isn't noise.

## Phase 3: Invocation and integrations

Right now Horizon *recommends*, and callers must remember to report outcomes.
Feedback coverage is the weak spot of the whole loop.

- **Horizon calls the agent** (REST first, then MCP): records latency, cost and
  status automatically, enforces `timeout_seconds`, and falls back to the
  next-ranked candidate on failure.
- Framework adapters wherever multi-agent routing already happens: LangGraph,
  CrewAI, OpenAI Agents SDK, Claude Agent SDK, MCP clients.
- TypeScript SDK.
- Docs site built on the quickstart, plus one worked end-to-end example project.

**Exit:** most executions from active orgs are recorded automatically rather
than hand-reported.

## Phase 4: Monetize and raise

- Usage metering and plan enforcement. `PLAN_LIMITS` is published via the API
  but nothing meters against it.
- Stripe billing against the settled table in `base/pricing.md`
  ($0 / $29 / $249 / custom, metered on routed decisions).
- Minimal dashboard: keys, usage, the Phase 2 lift chart per org.
- Pitch deck built around the real-traffic lift chart. Seed outreach.

**Exit:** paying customers, plus a funded round or a clear decision not to raise.

## Later: only when customers ask

- **Shared priors across orgs** for widely used third-party agents, so a new
  org's cold start isn't blank. This is the network-effect version of the
  moat, but it breaks strict tenant isolation, so it needs explicit opt-in,
  aggregation only, and a written privacy model first.
- Memory decay and pruning (`accessed_at` / `access_count` are already tracked)
- More embedding providers behind `EmbeddingProvider` (Voyage, Cohere, local)
- Multi-agent workflows: parallel/sequential calls, result synthesis (PRD REQ-003/004)
- RBAC and teams, audit log export, SOC 2, multi-region, self-hosted option
- A2A and gRPC agent protocols

## Not planned

These come from `prd.md` or the old `.cursor/plans/` and weren't adopted. Revisit
only with evidence:

- Sapentia as a separate product from Horizon
- A separate vector database (Pinecone/Qdrant/Weaviate). pgvector with HNSW is the choice until it measurably isn't enough.
- Cloudflare Workers edge deployment, Kubernetes, Redis. None has a current need.
- An agent marketplace
- Memory-only positioning ("the memory layer your AI agents deserve")
