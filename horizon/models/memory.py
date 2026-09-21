"""Semantic memories — the storage half of the product."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from horizon.config.settings import get_settings
from horizon.models.base import Base, Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from horizon.models.organization import Organization

EMBEDDING_DIM = get_settings().embedding_dimensions


class Memory(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "memories"

    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    # Namespacing. `collection` isolates agents/projects within one org.
    collection: Mapped[str] = mapped_column(
        String(128), default="default", nullable=False, index=True
    )
    context_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    meta: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    access_count: Mapped[int] = mapped_column(default=0, nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="memories")

    def __repr__(self) -> str:
        return f"<Memory id={self.id} collection={self.collection!r} user_id={self.user_id!r}>"


# Composite indexes matching the actual query shapes: every read is org-scoped.
Index("ix_memories_org_collection", Memory.org_id, Memory.collection)
Index("ix_memories_org_user", Memory.org_id, Memory.user_id)
Index("ix_memories_org_session", Memory.org_id, Memory.session_id)
Index("ix_memories_org_created_desc", Memory.org_id, Memory.created_at.desc())

# HNSW beats IVFFlat here: no training step, and recall stays good as rows are
# inserted continuously (which is the whole access pattern for a memory store).
Index(
    "ix_memories_embedding_hnsw",
    Memory.embedding,
    postgresql_using="hnsw",
    postgresql_with={"m": 16, "ef_construction": 64},
    postgresql_ops={"embedding": "vector_cosine_ops"},
)
