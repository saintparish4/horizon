"""Tenants and their API keys."""

import dataclasses
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from horizon.models.base import Base, Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    # Import-time only: models/memory.py imports this module, so a runtime
    # import here would be circular. The mapper resolves the string lazily.
    from horizon.models.memory import Memory


class PlanType(enum.StrEnum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclasses.dataclass(frozen=True)
class PlanLimits:
    """
    What a plan includes. Mirrors the published table in `base/pricing.md`;
    change both together.

    Billing meters **routed decisions**, not stored memories. Memory is a
    commodity that exports cleanly, so pricing it invites a race to zero;
    a routing decision is the unit that carries the value this product adds.

    `history_days` is a real product lever rather than an artificial one: the
    router's evidence has a 30-day half-life, so a 30-day window already
    captures most of the signal and each step up buys a genuinely longer memory.
    """

    monthly_routed_decisions: int
    stored_memories: int
    history_days: int | None  # None = retained indefinitely
    overage_usd_per_1k: float | None  # None = hard stop at the included amount
    monthly_usd: float | None  # None = negotiated


# Nothing meters usage against these yet (roadmap Phase 4). They are returned by
# GET /v1/organizations/me so a caller can see the shape of their plan.
PLAN_LIMITS: dict[PlanType, PlanLimits] = {
    PlanType.FREE: PlanLimits(10_000, 50_000, 30, None, 0.0),
    PlanType.STARTER: PlanLimits(100_000, 500_000, 90, 0.50, 29.0),
    PlanType.PRO: PlanLimits(1_500_000, 5_000_000, 396, 0.30, 249.0),
    PlanType.ENTERPRISE: PlanLimits(1_000_000_000, 1_000_000_000, None, None, None),
}


class Organization(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    plan: Mapped[PlanType] = mapped_column(String(32), default=PlanType.FREE, nullable=False)

    api_keys: Mapped[list["APIKey"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    memories: Mapped[list["Memory"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )

    @property
    def limits(self) -> PlanLimits:
        return PLAN_LIMITS[PlanType(self.plan)]

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name!r} plan={self.plan}>"


class APIKey(UUIDPrimaryKey, Timestamps, Base):
    """
    An API key is stored only as a peppered SHA-256 hash. The plaintext is
    returned once, at creation, and is not recoverable afterwards.

    `prefix` is the first `PREFIX_DISPLAY_LEN` (16) chars of the plaintext, kept
    so the dashboard can show `hzn_live_a1b2c2...` without holding the secret.
    """

    __tablename__ = "api_keys"

    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), default="default", nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    prefix: Mapped[str] = mapped_column(String(16), nullable=False)

    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = relationship(back_populates="api_keys")

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None

    def __repr__(self) -> str:
        return f"<APIKey id={self.id} prefix={self.prefix!r} active={self.is_active}>"
