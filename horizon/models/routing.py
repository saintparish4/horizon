"""
Routing decisions — what the router recommended, before anyone acted on it.

`/v1/route` used to be stateless: it answered and forgot. That left two holes.
A reported outcome carried whatever `routing_reason` the client chose to send,
so the audit trail was only as trustworthy as the caller; and nothing recorded
whether the caller actually used the recommendation, so real traffic could
never distinguish "the router was wrong" from "the router was overruled".

Persisting the decision closes both, and makes the stored task embedding
reusable so reporting an outcome costs zero extra embedding calls.
"""

import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Float, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from horizon.models.base import Base, Timestamps, UUIDPrimaryKey
from horizon.models.memory import EMBEDDING_DIM


class RoutingDecision(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "routing_decisions"

    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Nullable so a decision survives its agent being removed; the org cascade
    # is what actually reclaims these rows.
    selected_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    task: Mapped[str] = mapped_column(Text, nullable=False)
    task_embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    exploring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # The full per-candidate breakdown, as returned to the caller.
    candidates: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<RoutingDecision id={self.id} agent={self.selected_agent_id} "
            f"exploring={self.exploring}>"
        )


Index(
    "ix_routing_decisions_org_created_desc",
    RoutingDecision.org_id,
    RoutingDecision.created_at.desc(),
)
