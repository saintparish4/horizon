"""
Memory-aware agent routing.

The premise: which agent should handle a task is itself a question best
answered from memory. For a new task we find semantically similar tasks this
org has already run, look at what actually happened, and rank agents by
evidence rather than by a static rule table.

Scoring, per candidate agent:

    score = w_evidence * evidence + w_capability * capability - w_cost * cost

  evidence    optimistic estimate of how well this agent handles tasks like
              this one, from a Beta posterior over similar past executions
  capability  cosine similarity between the task and the agent's declared
              capabilities; carries routing before history exists (cold start)
  cost        normalized declared cost, as a tie-breaker only

This is a contextual bandit, so `evidence` must be optimistic rather than a
plain average. Ranking on the observed mean alone is self-reinforcing: an agent
only accrues history for tasks it already wins, so the first adequate agent
locks in and a genuinely better one is never tried. Concretely, with a mediocre
incumbent at 0.52 and w_evidence=0.6, an untried agent would need a capability
advantage above 1.0 to displace it — impossible, since cosine similarity is
bounded at 1.

So each agent gets a Beta(1+wins, 1+losses) posterior over similar tasks and is
scored at `mean + z * sd`. An untried agent sits near 0.79 (uniform prior, wide)
and outranks a known-mediocre one; as evidence accumulates the interval narrows
onto the true rate, and exploration stops on its own.

`confidence` reports the *exploitation* view — posterior mean and support — so a
low value plus `exploring=True` tells a caller the router is still learning
rather than that it is confused.
"""

import math
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.models import Agent, Execution, ExecutionStatus, RoutingDecision
from horizon.services.embeddings import get_embeddings

log = structlog.get_logger(__name__)

W_EVIDENCE = 0.6
W_CAPABILITY = 0.3
W_COST = 0.1

# Past executions below this similarity tell us nothing about the new task.
#
# Measured, not guessed — but measured under the wrong conditions, and that
# caveat matters. `make similarity` reports the two distributions this value has
# to separate: pairs of tasks from the same family (which should count as
# evidence) and pairs from different families (which should not). Under the
# benchmark's lexical embeddings with templated phrasing, same-family pairs sit
# at a median of 0.833 and different-family pairs peak at 0.199, so anything
# from 0.40 to 0.72 separates them perfectly; 0.75 is slightly conservative,
# keeping 92% of real evidence and admitting none of the unrelated kind.
#
# That gap is an artefact of lexical overlap. Paraphrase the same tasks and
# same-family similarity collapses to a median of 0.261 — indistinguishable from
# unrelated work — and 0.75 keeps only 24% of genuine evidence. A real embedding
# model scores short related strings far higher and in a much narrower band, so
# this number is almost certainly wrong for production traffic in one direction
# or the other. Run `make similarity-openai` and reset it from that data before
# anyone routes real work. Tracked in base/next-steps.md.
EVIDENCE_MIN_SIMILARITY = 0.75
# How many similar past executions to consult.
EVIDENCE_LIMIT = 50
# Evidence half-life. A 30-day-old outcome counts half as much as today's:
# agents get rewritten, models get swapped, and stale wins should fade.
EVIDENCE_HALFLIFE_DAYS = 30.0
# Evidence weight needed before we call a routing decision well-supported.
CONFIDENCE_SATURATION = 5.0
# Standard deviations of optimism on the posterior. Higher explores longer.
# 1.0 keeps an untried agent (Beta(1,1): mean .50, sd .29) at ~0.79 — ahead of a
# known-mediocre incumbent, behind a known-good one.
EXPLORATION_Z = 1.0
# Uniform Beta prior: no opinion about an agent before any evidence arrives.
PRIOR_ALPHA = 1.0
PRIOR_BETA = 1.0


@dataclass
class Candidate:
    agent: Agent
    score: float = 0.0
    capability: float = 0.0
    cost_penalty: float = 0.0
    sample_size: int = 0

    # Beta posterior over success on similar tasks, in evidence-weight units.
    wins: float = 0.0
    losses: float = 0.0

    @property
    def support(self) -> float:
        """Total evidence weight behind this candidate."""
        return self.wins + self.losses

    @property
    def evidence_mean(self) -> float:
        """Posterior mean — the exploitation estimate."""
        a = PRIOR_ALPHA + self.wins
        b = PRIOR_BETA + self.losses
        return a / (a + b)

    @property
    def evidence_sd(self) -> float:
        """Posterior standard deviation — how unsure we are."""
        a = PRIOR_ALPHA + self.wins
        b = PRIOR_BETA + self.losses
        total = a + b
        return math.sqrt((a * b) / (total * total * (total + 1)))

    @property
    def evidence(self) -> float:
        """Optimistic upper bound. This is what ranking uses."""
        return min(1.0, self.evidence_mean + EXPLORATION_Z * self.evidence_sd)

    def reason(self) -> dict[str, Any]:
        return {
            "agent_id": str(self.agent.id),
            "agent_name": self.agent.name,
            "score": round(self.score, 4),
            "evidence": round(self.evidence, 4),
            "evidence_mean": round(self.evidence_mean, 4),
            "evidence_sd": round(self.evidence_sd, 4),
            "capability": round(self.capability, 4),
            "cost_penalty": round(self.cost_penalty, 4),
            "sample_size": self.sample_size,
        }


@dataclass
class RoutingResult:
    """One scoring pass, in memory. `save_decision` persists it."""

    selected: Agent | None
    confidence: float
    candidates: list[Candidate] = field(default_factory=list)
    task_embedding: list[float] | None = None
    exploring: bool = False

    def reason(self) -> dict[str, Any]:
        return {
            "selected_agent_id": str(self.selected.id) if self.selected else None,
            "confidence": round(self.confidence, 4),
            "exploring": self.exploring,
            "weights": {
                "evidence": W_EVIDENCE,
                "capability": W_CAPABILITY,
                "cost": W_COST,
            },
            "exploration_z": EXPLORATION_Z,
            "considered": [c.reason() for c in self.candidates],
        }


def _outcome_value(execution: Execution) -> float:
    """Map an execution to 0.0-1.0. Explicit feedback wins over status."""
    if execution.quality_score is not None:
        return max(0.0, min(1.0, execution.quality_score))
    return 1.0 if execution.status == ExecutionStatus.SUCCESS else 0.0


def _recency_weight(created_at: datetime, now: datetime) -> float:
    age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)
    return 0.5 ** (age_days / EVIDENCE_HALFLIFE_DAYS)


async def route(
    db: AsyncSession,
    org_id: uuid.UUID,
    task: str,
    *,
    allowed_agent_ids: list[uuid.UUID] | None = None,
    required_capabilities: list[str] | None = None,
    min_similarity: float = EVIDENCE_MIN_SIMILARITY,
) -> RoutingResult:
    """
    Pick the agent most likely to handle `task` well.

    `min_similarity` sets how alike a past task must be to count as evidence.
    Workloads with tightly-templated tasks can raise it; workloads with free-form
    phrasing need it lower or no history will ever qualify.
    """
    task_embedding = await get_embeddings().embed_one(task)

    agents = await _eligible_agents(db, org_id, allowed_agent_ids, required_capabilities)
    if not agents:
        return RoutingResult(selected=None, confidence=0.0, task_embedding=task_embedding)

    candidates = {a.id: Candidate(agent=a) for a in agents}

    _score_capability(candidates, task_embedding)
    await _score_evidence(db, org_id, task_embedding, candidates, min_similarity)
    _score_cost(candidates)

    for c in candidates.values():
        c.score = W_EVIDENCE * c.evidence + W_CAPABILITY * c.capability - W_COST * c.cost_penalty

    ranked = sorted(candidates.values(), key=lambda c: c.score, reverse=True)
    best = ranked[0]

    # An exploration pick is one the optimism bonus produced: the agent we would
    # have chosen on posterior means alone is a different one. Callers that
    # cannot tolerate a gamble on a given request can check this and override.
    greedy = max(candidates.values(), key=_greedy_score)
    exploring = greedy.agent.id != best.agent.id

    # Confidence is the exploitation view: how much evidence backs the winner,
    # and how clearly it leads on posterior means. A wide-interval exploration
    # pick should read as low confidence, not high.
    support = 1 - math.exp(-best.support / CONFIDENCE_SATURATION)
    means = sorted((c.evidence_mean for c in candidates.values()), reverse=True)
    margin = (means[0] - means[1]) if len(means) > 1 else means[0]
    confidence = max(0.0, min(1.0, 0.5 * support + 0.5 * min(1.0, max(0.0, margin) * 2)))

    result = RoutingResult(
        selected=best.agent,
        confidence=confidence,
        candidates=ranked,
        task_embedding=task_embedding,
        exploring=exploring,
    )
    log.info(
        "routed",
        org_id=str(org_id),
        agent=best.agent.name,
        confidence=round(confidence, 3),
        exploring=exploring,
        sample_size=best.sample_size,
    )
    return result


async def save_decision(
    db: AsyncSession, org_id: uuid.UUID, task: str, result: RoutingResult
) -> RoutingDecision:
    """
    Persist a recommendation so the outcome can be linked back to it.

    Written before the caller acts, which is the point: the stored reason is
    the server's own record rather than whatever the client later claims, and
    the stored embedding means reporting the outcome costs no second embed.
    """
    decision = RoutingDecision(
        org_id=org_id,
        selected_agent_id=result.selected.id if result.selected else None,
        task=task,
        task_embedding=result.task_embedding,
        confidence=result.confidence,
        exploring=result.exploring,
        candidates=result.reason(),
    )
    db.add(decision)
    await db.flush()
    return decision


def _greedy_score(c: Candidate) -> float:
    """Score with the optimism bonus removed — pure exploitation."""
    return W_EVIDENCE * c.evidence_mean + W_CAPABILITY * c.capability - W_COST * c.cost_penalty


async def _eligible_agents(
    db: AsyncSession,
    org_id: uuid.UUID,
    allowed_agent_ids: list[uuid.UUID] | None,
    required_capabilities: list[str] | None,
) -> list[Agent]:
    stmt = select(Agent).where(Agent.org_id == org_id, Agent.enabled.is_(True))
    if allowed_agent_ids:
        stmt = stmt.where(Agent.id.in_(allowed_agent_ids))
    if required_capabilities:
        stmt = stmt.where(Agent.capabilities.contains(required_capabilities))
    # Ordered so that exact score ties break the same way every time. Without
    # it the winner depends on whatever order Postgres happened to return, and
    # the benchmark stops being reproducible.
    stmt = stmt.order_by(Agent.created_at, Agent.id)
    return list((await db.execute(stmt)).scalars().all())


def _score_capability(candidates: dict[uuid.UUID, Candidate], task_embedding: list[float]) -> None:
    """Cosine similarity between task and each agent's capability embedding."""
    for c in candidates.values():
        emb = c.agent.capability_embedding
        if emb is None:
            continue
        c.capability = max(0.0, _cosine(task_embedding, list(emb)))


async def _score_evidence(
    db: AsyncSession,
    org_id: uuid.UUID,
    task_embedding: list[float],
    candidates: dict[uuid.UUID, Candidate],
    min_similarity: float = EVIDENCE_MIN_SIMILARITY,
) -> None:
    """Weighted outcome average over semantically similar past executions."""
    distance = Execution.task_embedding.cosine_distance(task_embedding)
    stmt = (
        select(Execution, (1 - distance).label("similarity"))
        .where(
            Execution.org_id == org_id,
            Execution.agent_id.in_(list(candidates.keys())),
            Execution.task_embedding.is_not(None),
            distance < (1 - min_similarity),
        )
        .order_by(distance)
        .limit(EVIDENCE_LIMIT)
    )
    rows = (await db.execute(stmt)).all()

    now = datetime.now(UTC)
    for execution, similarity in rows:
        weight = float(similarity) * _recency_weight(execution.created_at, now)
        if weight <= 0:
            continue
        c = candidates[execution.agent_id]
        c.sample_size += 1
        # A partial-credit outcome splits its weight across both sides of the
        # posterior, so quality_score=0.7 reads as 70% of a win.
        outcome = _outcome_value(execution)
        c.wins += weight * outcome
        c.losses += weight * (1.0 - outcome)


def _score_cost(candidates: dict[uuid.UUID, Candidate]) -> None:
    """Normalize declared cost across the candidate set into a 0-1 penalty."""
    costs = [c.agent.cost_per_call_usd for c in candidates.values()]
    hi = max(costs)
    if hi <= 0:
        return
    for c in candidates.values():
        c.cost_penalty = c.agent.cost_per_call_usd / hi


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0
