"""Agent registry and execution history — the routing half of the product."""

import enum
import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from horizon.models.base import Base, Timestamps, UUIDPrimaryKey
from horizon.models.memory import EMBEDDING_DIM


class Protocol(enum.StrEnum):
    REST = "rest"
    MCP = "mcp"
    GRPC = "grpc"


class ExecutionStatus(enum.StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class Agent(UUIDPrimaryKey, Timestamps, Base):
    """A registered agent an org can route work to."""

    __tablename__ = "agents"
    __table_args__ = (UniqueConstraint("org_id", "name", name="uq_agents_org_name"),)

    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    endpoint: Mapped[str] = mapped_column(String(1024), nullable=False)
    protocol: Mapped[str] = mapped_column(String(16), default=Protocol.REST, nullable=False)

    capabilities: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    # Embedding of "name + description + capabilities". Used for the cold-start
    # path, before this agent has any execution history to route on.
    capability_embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )

    # Operator-declared hints, used for cost-aware tie-breaking.
    cost_per_call_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    timeout_seconds: Mapped[float] = mapped_column(Float, default=30.0, nullable=False)

    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    executions: Mapped[list["Execution"]] = relationship(
        back_populates="agent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Agent id={self.id} name={self.name!r} enabled={self.enabled}>"


class Execution(UUIDPrimaryKey, Timestamps, Base):
    """
    One routed task and how it turned out.

    This table is the product's actual moat: it is memory *about routing*, not
    about the user. Given a new task, we embed it, find semantically similar
    past executions, and route to whatever actually worked — so accuracy
    improves with volume instead of staying flat.
    """

    __tablename__ = "executions"

    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    task: Mapped[str] = mapped_column(Text, nullable=False)
    task_embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    latency_ms: Mapped[int] = mapped_column(default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # 0.0-1.0. Set by explicit developer feedback, or defaulted from status.
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # The decision this outcome answers. Nullable: callers may report an
    # execution they never asked us to route, and older clients predate it.
    decision_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("routing_decisions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # Did the caller run the agent we recommended? None when there is no linked
    # decision to compare against. This is what separates "the router was wrong"
    # from "the router was overruled" once real traffic arrives.
    followed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Why this agent was picked — the audit trail. Copied from the linked
    # decision when there is one, so the client cannot forge it.
    routing_reason: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    agent: Mapped[Agent] = relationship(back_populates="executions")

    def __repr__(self) -> str:
        return f"<Execution id={self.id} agent_id={self.agent_id} status={self.status}>"


Index("ix_executions_org_agent", Execution.org_id, Execution.agent_id)
Index("ix_executions_org_created_desc", Execution.org_id, Execution.created_at.desc())
Index(
    "ix_executions_task_embedding_hnsw",
    Execution.task_embedding,
    postgresql_using="hnsw",
    postgresql_with={"m": 16, "ef_construction": 64},
    postgresql_ops={"task_embedding": "vector_cosine_ops"},
)
Index(
    "ix_agents_capability_embedding_hnsw",
    Agent.capability_embedding,
    postgresql_using="hnsw",
    postgresql_with={"m": 16, "ef_construction": 64},
    postgresql_ops={"capability_embedding": "vector_cosine_ops"},
)
