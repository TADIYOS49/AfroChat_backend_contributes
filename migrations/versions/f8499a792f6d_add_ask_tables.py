"""add-ask-tables

Revision ID: f8499a792f6d
Revises: 4a32ea9f6196
Create Date: 2024-03-05 13:33:45.498093

"""
from alembic import op
import sqlalchemy as sa

from app.constants import LLMModels


# revision identifiers, used by Alembic.
revision = "f8499a792f6d"
down_revision = "4a32ea9f6196"
branch_labels = None
depends_on = None


def upgrade():
    # Create tables in the order of their dependencies
    op.create_table(
        "ask_session",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_message", sa.String(10000), nullable=False),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("is_pinned", sa.Boolean, server_default="false", nullable=False),
        sa.Column("total_tokens", sa.Integer, server_default="0", nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "ask_message",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question", sa.String(10000), nullable=False),
        sa.Column("summary", sa.String(10000), nullable=False),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("ask_session_id", sa.UUID(), nullable=False),
        sa.Column("token_usage", sa.Integer, nullable=False),
        sa.Column(
            "llm_model",
            sa.String(100),
            server_default=LLMModels.GEMINIPRO.value,
            nullable=False,
        ),
        sa.Column("message_from", sa.Integer, nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ask_session_id"], ["ask_session.id"], ondelete="CASCADE"
        ),
    )

    op.create_table(
        "sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ask_message_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(10000), nullable=False),
        sa.Column("short_description", sa.String(10000), nullable=False),
        sa.Column("URL", sa.String(10000), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ask_message_id"], ["ask_message.id"], ondelete="CASCADE"
        ),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ask_message_id", sa.UUID(), nullable=False),
        sa.Column("question", sa.String(10000), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ask_message_id"], ["ask_message.id"], ondelete="CASCADE"
        ),
    )

    # Create indexes
    op.create_index(
        op.f("ix_ask_message_ask_session_id"), "ask_message", ["ask_session_id"]
    )
    op.create_index(op.f("ix_sources_ask_message_id"), "sources", ["ask_message_id"])
    op.create_index(
        op.f("ix_recommendations_ask_message_id"), "recommendations", ["ask_message_id"]
    )
    op.create_index(op.f("ix_source_id"), "sources", ["id"])  # New index for source.id
    op.create_index(
        op.f("ix_recommendations_id"), "recommendations", ["id"]
    )  # New index for recommended.id
    op.create_index(
        op.f("ix_ask_message_id"), "ask_message", ["id"]
    )  # New index for ask_message.id
    op.create_index(
        op.f("ix_ask_session_id"), "ask_session", ["id"]
    )  # New index for ask_session.id


def downgrade():
    # Drop indexes in the reverse order of their creation (unchanged)
    op.drop_index(op.f("ix_ask_session_id"), table_name="ask_session")
    op.drop_index(op.f("ix_ask_message_id"), table_name="ask_message")
    op.drop_index(op.f("ix_recommendations_id"), table_name="recomendations")
    op.drop_index(op.f("ix_source_id"), table_name="sources")
    op.drop_index(
        op.f("ix_recommendations_ask_message_id"), table_name="recommendations"
    )
    op.drop_index(op.f("ix_sources_ask_message_id"), table_name="sources")
    op.drop_index(op.f("ix_ask_message_ask_session_id"), table_name="ask_message")

    # Drop tables in the reverse order of their creation (unchanged)
    op.drop_table("recommendations")
    op.drop_table("sources")
    op.drop_table("ask_message")
    op.drop_table("ask_session")
