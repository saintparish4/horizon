"""Initial schema: organizations, api_keys, memories, agents, executions

Revision ID: 0001
Revises:
Create Date: 2026-09-04
"""

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

EMBEDDING_DIM = 1536


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("plan", sa.String(32), nullable=False, server_default="free"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_organizations_email", "organizations", ["email"], unique=True)
    op.create_index("ix_organizations_created_at", "organizations", ["created_at"])

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False, server_default="default"),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("prefix", sa.String(16), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)
    op.create_index("ix_api_keys_org_id", "api_keys", ["org_id"])
    op.create_index("ix_api_keys_created_at", "api_keys", ["created_at"])

    op.create_table(
        "memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(EMBEDDING_DIM), nullable=True),
        sa.Column("collection", sa.String(128), nullable=False, server_default="default"),
        sa.Column("context_type", sa.String(50), nullable=True),
        sa.Column("user_id", sa.String(255), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column(
            "accessed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("access_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_memories_org_id", "memories", ["org_id"])
    op.create_index("ix_memories_collection", "memories", ["collection"])
    op.create_index("ix_memories_context_type", "memories", ["context_type"])
    op.create_index("ix_memories_user_id", "memories", ["user_id"])
    op.create_index("ix_memories_session_id", "memories", ["session_id"])
    op.create_index("ix_memories_created_at", "memories", ["created_at"])
    op.create_index("ix_memories_org_collection", "memories", ["org_id", "collection"])
    op.create_index("ix_memories_org_user", "memories", ["org_id", "user_id"])
    op.create_index("ix_memories_org_session", "memories", ["org_id", "session_id"])
    op.execute("CREATE INDEX ix_memories_org_created_desc ON memories (org_id, created_at DESC)")
    op.execute(
        "CREATE INDEX ix_memories_embedding_hnsw ON memories "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("endpoint", sa.String(1024), nullable=False),
        sa.Column("protocol", sa.String(16), nullable=False, server_default="rest"),
        sa.Column("capabilities", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("capability_embedding", pgvector.sqlalchemy.Vector(EMBEDDING_DIM), nullable=True),
        sa.Column("cost_per_call_usd", sa.Float, nullable=False, server_default="0"),
        sa.Column("timeout_seconds", sa.Float, nullable=False, server_default="30"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("org_id", "name", name="uq_agents_org_name"),
    )
    op.create_index("ix_agents_org_id", "agents", ["org_id"])
    op.create_index("ix_agents_created_at", "agents", ["created_at"])
    op.execute(
        "CREATE INDEX ix_agents_capability_embedding_hnsw ON agents "
        "USING hnsw (capability_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )

    op.create_table(
        "executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("task", sa.Text, nullable=False),
        sa.Column("task_embedding", pgvector.sqlalchemy.Vector(EMBEDDING_DIM), nullable=True),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Float, nullable=False, server_default="0"),
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("feedback_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("routing_reason", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_executions_org_id", "executions", ["org_id"])
    op.create_index("ix_executions_agent_id", "executions", ["agent_id"])
    op.create_index("ix_executions_status", "executions", ["status"])
    op.create_index("ix_executions_created_at", "executions", ["created_at"])
    op.create_index("ix_executions_org_agent", "executions", ["org_id", "agent_id"])
    op.execute(
        "CREATE INDEX ix_executions_org_created_desc ON executions (org_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX ix_executions_task_embedding_hnsw ON executions "
        "USING hnsw (task_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    op.drop_table("executions")
    op.drop_table("agents")
    op.drop_table("memories")
    op.drop_table("api_keys")
    op.drop_table("organizations")
