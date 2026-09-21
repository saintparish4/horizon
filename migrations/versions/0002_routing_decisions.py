"""Routing decisions, and the link from an execution back to one

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-20

`/v1/route` previously stored nothing, so an execution's `routing_reason` was
whatever the client sent and nothing recorded whether the recommendation was
actually followed. This adds the server-side record and the link.
"""

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

EMBEDDING_DIM = 1536


def upgrade() -> None:
    op.create_table(
        "routing_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "selected_agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("task", sa.Text, nullable=False),
        sa.Column("task_embedding", pgvector.sqlalchemy.Vector(EMBEDDING_DIM), nullable=True),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0"),
        sa.Column("exploring", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("candidates", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_routing_decisions_org_id", "routing_decisions", ["org_id"])
    op.create_index(
        "ix_routing_decisions_selected_agent_id", "routing_decisions", ["selected_agent_id"]
    )
    op.create_index("ix_routing_decisions_created_at", "routing_decisions", ["created_at"])
    op.execute(
        "CREATE INDEX ix_routing_decisions_org_created_desc "
        "ON routing_decisions (org_id, created_at DESC)"
    )

    op.add_column(
        "executions",
        sa.Column(
            "decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("routing_decisions.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    # Nullable on purpose: NULL means "no linked decision", which is different
    # from "the caller overrode us" (false).
    op.add_column("executions", sa.Column("followed", sa.Boolean, nullable=True))
    op.create_index("ix_executions_decision_id", "executions", ["decision_id"])


def downgrade() -> None:
    op.drop_index("ix_executions_decision_id", table_name="executions")
    op.drop_column("executions", "followed")
    op.drop_column("executions", "decision_id")
    op.drop_table("routing_decisions")
