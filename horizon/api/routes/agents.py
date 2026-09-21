"""Agent registry, routing, and execution feedback."""

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from horizon.api.deps import CurrentOrg, DbSession
from horizon.models import Agent, Execution, RoutingDecision
from horizon.schemas.agent import (
    AgentCreate,
    AgentOut,
    ExecutionCreate,
    ExecutionOut,
    RouteRequest,
    RouteResponse,
)
from horizon.services import router as routing
from horizon.services.embeddings import get_embeddings

router = APIRouter(prefix="/v1", tags=["agents"])


@router.post("/agents", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def register_agent(payload: AgentCreate, org: CurrentOrg, db: DbSession) -> AgentOut:
    existing = await db.execute(
        select(Agent).where(Agent.org_id == org.id, Agent.name == payload.name)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail=f"Agent {payload.name!r} already registered"
        )

    # Embed the agent's self-description so it can be routed to before it has
    # any execution history.
    profile = " ".join(
        filter(None, [payload.name, payload.description, " ".join(payload.capabilities)])
    )
    agent = Agent(
        org_id=org.id,
        name=payload.name,
        description=payload.description,
        endpoint=payload.endpoint,
        protocol=payload.protocol.value,
        capabilities=payload.capabilities,
        capability_embedding=await get_embeddings().embed_one(profile),
        cost_per_call_usd=payload.cost_per_call_usd,
        timeout_seconds=payload.timeout_seconds,
        config=payload.config,
    )
    db.add(agent)
    await db.flush()
    # Serialize inside the session — see the note in routes/memories.py.
    return AgentOut.model_validate(agent)


@router.get("/agents", response_model=list[AgentOut])
async def list_agents(org: CurrentOrg, db: DbSession) -> list[AgentOut]:
    stmt = select(Agent).where(Agent.org_id == org.id).order_by(Agent.created_at.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return [AgentOut.model_validate(a) for a in rows]


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disable_agent(agent_id: uuid.UUID, org: CurrentOrg, db: DbSession) -> None:
    agent = await _owned_agent(db, org.id, agent_id)
    # Soft disable: hard-deleting would take the execution history with it, and
    # that history is what makes routing improve.
    agent.enabled = False
    await db.flush()


@router.post("/route", response_model=RouteResponse)
async def route_task(payload: RouteRequest, org: CurrentOrg, db: DbSession) -> RouteResponse:
    result = await routing.route(
        db,
        org.id,
        payload.task,
        allowed_agent_ids=payload.allowed_agent_ids or None,
        required_capabilities=payload.required_capabilities or None,
        min_similarity=(
            payload.min_similarity
            if payload.min_similarity is not None
            else routing.EVIDENCE_MIN_SIMILARITY
        ),
    )
    if result.selected is None:
        # Nothing to record: a decision row with no agent would be noise in the
        # audit trail and in the usage meter.
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No eligible agents. Register an agent, or relax the constraints.",
        )

    decision = await routing.save_decision(db, org.id, payload.task, result)
    return RouteResponse(
        decision_id=decision.id,
        selected_agent=AgentOut.model_validate(result.selected),
        confidence=result.confidence,
        reason=result.reason(),
    )


@router.post("/executions", response_model=ExecutionOut, status_code=status.HTTP_201_CREATED)
async def record_execution(
    payload: ExecutionCreate, org: CurrentOrg, db: DbSession
) -> ExecutionOut:
    """
    Report how a routed task turned out. This is the feedback loop: without it
    the router never learns, and routing stays capability-similarity only.
    """
    await _owned_agent(db, org.id, payload.agent_id)

    decision = None
    if payload.decision_id is not None:
        decision = await _owned_decision(db, org.id, payload.decision_id)

    if decision is not None:
        # Everything about the task comes from our own record. The client can
        # only tell us the outcome, which is the one thing it actually knows.
        task = decision.task
        embedding = decision.task_embedding
        reason = decision.candidates
        followed = decision.selected_agent_id == payload.agent_id
        if embedding is None:  # pragma: no cover - only if a decision predates embedding
            embedding = await get_embeddings().embed_one(task)
    else:
        assert payload.task is not None  # guaranteed by ExecutionCreate's validator
        task = payload.task
        embedding = await get_embeddings().embed_one(task)
        reason = payload.routing_reason
        followed = None

    execution = Execution(
        org_id=org.id,
        agent_id=payload.agent_id,
        decision_id=payload.decision_id,
        followed=followed,
        task=task,
        task_embedding=embedding,
        status=payload.status.value,
        latency_ms=payload.latency_ms,
        cost_usd=payload.cost_usd,
        quality_score=payload.quality_score,
        routing_reason=reason,
        error=payload.error,
    )
    db.add(execution)
    await db.flush()
    return ExecutionOut.model_validate(execution)


@router.get("/executions", response_model=list[ExecutionOut])
async def list_executions(
    org: CurrentOrg,
    db: DbSession,
    agent_id: uuid.UUID | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[ExecutionOut]:
    stmt = select(Execution).where(Execution.org_id == org.id)
    if agent_id is not None:
        stmt = stmt.where(Execution.agent_id == agent_id)
    stmt = stmt.order_by(Execution.created_at.desc()).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()
    return [ExecutionOut.model_validate(e) for e in rows]


async def _owned_agent(db: DbSession, org_id: uuid.UUID, agent_id: uuid.UUID) -> Agent:
    stmt = select(Agent).where(Agent.id == agent_id, Agent.org_id == org_id)
    agent = (await db.execute(stmt)).scalar_one_or_none()
    if agent is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


async def _owned_decision(
    db: DbSession, org_id: uuid.UUID, decision_id: uuid.UUID
) -> RoutingDecision:
    """Org-scoped even though the id is a primary key — a guessed UUID must not
    let one tenant attach outcomes to another tenant's decision."""
    stmt = select(RoutingDecision).where(
        RoutingDecision.id == decision_id, RoutingDecision.org_id == org_id
    )
    decision = (await db.execute(stmt)).scalar_one_or_none()
    if decision is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Routing decision not found")
    return decision
