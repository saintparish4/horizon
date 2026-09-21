"""Self-service signup and API key management."""

import dataclasses
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import func, select

from horizon.api.deps import AppSettings, CurrentOrg, DbSession
from horizon.models import APIKey, Execution, Memory, Organization, PlanType, RoutingDecision
from horizon.services import api_keys

router = APIRouter(prefix="/v1", tags=["organizations"])


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr


class SignupResponse(BaseModel):
    org_id: str
    name: str
    plan: str
    api_key: str = Field(description="Shown once. Store it now — it cannot be retrieved again.")


class APIKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    prefix: str
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


class PlanLimitsOut(BaseModel):
    """The shape of the caller's plan. Mirrors `base/pricing.md`."""

    monthly_usd: float | None
    monthly_routed_decisions: int
    stored_memories: int
    history_days: int | None
    overage_usd_per_1k: float | None


class UsageResponse(BaseModel):
    """
    What this org has used and what its plan allows.

    Nothing is enforced against `limits` yet — metering is roadmap Phase 4 —
    but the counts are real, and they are the same numbers the accuracy chart
    is built from.
    """

    plan: str
    memories_stored: int
    routed_decisions_this_month: int
    executions_recorded: int
    executions_with_feedback: int
    limits: PlanLimitsOut


@router.post("/organizations", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, db: DbSession, settings: AppSettings) -> SignupResponse:
    """Open endpoint — this is where a caller gets their first API key."""
    existing = await db.execute(select(Organization).where(Organization.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

    org = Organization(name=payload.name, email=payload.email, plan=PlanType.FREE)
    db.add(org)
    await db.flush()

    plaintext = api_keys.generate_key()
    db.add(
        APIKey(
            org_id=org.id,
            name="default",
            key_hash=api_keys.hash_key(plaintext, settings.api_key_pepper),
            prefix=api_keys.display_prefix(plaintext),
        )
    )
    await db.flush()

    return SignupResponse(org_id=str(org.id), name=org.name, plan=org.plan, api_key=plaintext)


@router.get("/organizations/me", response_model=UsageResponse)
async def usage(org: CurrentOrg, db: DbSession) -> UsageResponse:
    async def _count(model, *extra) -> int:
        stmt = select(func.count()).select_from(model).where(model.org_id == org.id, *extra)
        return await db.scalar(stmt) or 0

    # Calendar month to date, which is how the plan is billed.
    month_start = func.date_trunc("month", func.now())
    return UsageResponse(
        plan=org.plan,
        memories_stored=await _count(Memory),
        routed_decisions_this_month=await _count(
            RoutingDecision, RoutingDecision.created_at >= month_start
        ),
        executions_recorded=await _count(Execution),
        executions_with_feedback=await _count(Execution, Execution.quality_score.is_not(None)),
        limits=PlanLimitsOut(**dataclasses.asdict(org.limits)),
    )


@router.post("/api-keys", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def rotate_key(org: CurrentOrg, db: DbSession, settings: AppSettings) -> SignupResponse:
    """Issue an additional key. Old keys keep working until explicitly revoked."""
    plaintext = api_keys.generate_key()
    db.add(
        APIKey(
            org_id=org.id,
            name=f"key-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            key_hash=api_keys.hash_key(plaintext, settings.api_key_pepper),
            prefix=api_keys.display_prefix(plaintext),
        )
    )
    await db.flush()
    return SignupResponse(org_id=str(org.id), name=org.name, plan=org.plan, api_key=plaintext)
