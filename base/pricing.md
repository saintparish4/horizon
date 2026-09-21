# Pricing

Decided **2026-09-20**, replacing the two conflicting tables in `prd.md`
($49/$199) and the old launch plan ($19/$79/$299). Neither of those was ever
adopted; this one is. The numbers live in code in `PLAN_LIMITS`
(`horizon/models/organization.py`) — change both together.

Nothing is metered or billed yet. This is the published shape, not a running
billing system; enforcement is roadmap Phase 4.

## The unit: routed decisions

Billing meters **routed decisions** — one `POST /v1/route` that returns an
agent. Not stored memories, not API calls in general.

Memory-as-a-service is a commodity. Mem0, Zep and Letta all sell it, it exports
cleanly, and pricing it invites a race to the bottom against products with more
funding. The routing decision is the thing that only gets better because of
history we hold, so it is the thing worth charging for. Storing memories is
capacity we bundle; deciding what to do with them is the product.

Reporting an outcome (`POST /v1/executions`) is **free**, deliberately. Feedback
coverage is the weakest link in the whole loop — a router with no outcomes
degrades to capability similarity. Charging for the one action that makes the
product work would be self-defeating.

## Plans

| | Free | Starter | Pro | Enterprise |
|---|---|---|---|---|
| **Monthly** | $0 | **$29** | **$249** | custom |
| Routed decisions included | 10,000 | 100,000 | 1,500,000 | custom |
| Overage per 1,000 | — (hard stop) | $0.50 | $0.30 | custom |
| Stored memories | 50,000 | 500,000 | 5,000,000 | custom |
| Execution history retained | 30 days | 90 days | 13 months | unlimited |
| Seats | unlimited | unlimited | unlimited | unlimited |
| Support | community | email | email, 1 business day | SLA |
| | | | | SSO, audit export, self-host |

Annual billing: two months free (~17% off), the standard discount.

### Why these numbers

- **Free at 10,000** matches where Mem0 (10,000 memories) and Zep (10,000
  credits) set theirs, so the tier reads as normal to anyone comparing.
- **Starter at $29** sits between Mem0's $19 and Zep's $25 Flex tier. Both
  competitors then jump hard — Mem0 to $249, Zep to $125 — so a single
  mid-tier is enough; a fourth paid tier would be inventing a decision the
  customer does not want to make.
- **Pro at $249** matches Mem0 Pro exactly. Landing on the same number as the
  best-known comparable makes the comparison about the product.
- **No per-seat pricing.** LangSmith charges $39/seat and that is the loudest
  complaint about it. Infrastructure billed per seat punishes exactly the
  behaviour we want — more engineers wiring more agents into the loop.
- **Overage falls with tier** ($0.50 → $0.30 per 1,000) so growing into a plan
  is always cheaper than bursting past a smaller one.

### Why retention is the other lever

`history_days` is not an artificial gate. Evidence in the router decays with a
30-day half-life, so a 30-day window already carries most of the usable signal
and each step up buys a genuinely longer memory — a year of history is worth
real money to a team with seasonal or slow-moving task mixes, and worth little
to someone prototyping. Gating something the customer can feel beats gating
something invented for the pricing page.

## Unit economics

One routed decision costs one embedding call plus one pgvector query. At
`text-embedding-3-small` rates ($0.02 / 1M tokens) a ~20-token task is about
$0.0000004, so 1.5M decisions ≈ **$0.60 of embeddings** against $249 of revenue.
Reporting the outcome reuses the stored embedding and costs nothing extra —
that is what the `routing_decisions` table bought.

The real cost is storage and index maintenance: 1.5M executions at 1536
dimensions × 4 bytes ≈ 9 GB of vectors before HNSW overhead. Retention limits
are what keep that bounded, which is the second reason they are a plan lever
rather than a sales tactic.

Margin is not the risk here. Adoption is.

## Deliberately not priced

- **Seats / users.** See above.
- **Stored memories** beyond a generous ceiling, for the commodity reason.
- **Executions reported.** Free forever.
- **Agents registered.** Registering more agents makes routing better, and
  therefore makes the product better. Never charge for it.

## Open questions

- Whether Free should hard-stop or degrade to capability-only routing. A hard
  stop is honest; degrading keeps the app alive and demonstrates precisely what
  the paid tier adds. Decide once there is a hosted instance to watch.
- Whether Enterprise should be priced on decisions at all, or on deployment.
- Whether a usage-only tier (no base fee, pure $/1k) wins the developers who
  bounce off any monthly minimum.

Comparables checked 2026-09-20: Mem0 (Hobby free / $19 Starter / $249 Pro),
Zep ($25 Flex, paid from $125, $375 Flex Plus), LangSmith (free Developer /
$39 per seat Plus, $2.50 per 1k extra traces).
