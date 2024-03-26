"""removed the old telegram database

Revision ID: 10a94fc24dad
Revises: 9320e3a6a3f9
Create Date: 2024-01-01 13:09:14.921695

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "10a94fc24dad"
down_revision = "9320e3a6a3f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("telegram_ask")
    op.drop_table("telegram_message")
    op.drop_table("telegram_conversation")
    op.drop_table("telegram_user")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "telegram_message",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("role", sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column(
            "content", sa.VARCHAR(length=100000), autoincrement=False, nullable=False
        ),
        sa.Column("token_usage", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "timestamp",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["telegram_conversation.id"],
            name="telegram_message_conversation_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="telegram_message_pkey"),
    )
    op.create_table(
        "telegram_user",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text("nextval('telegram_user_id_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "telegram_id", sa.VARCHAR(length=50), autoincrement=False, nullable=False
        ),
        sa.Column(
            "firstname", sa.VARCHAR(length=50), autoincrement=False, nullable=False
        ),
        sa.Column(
            "username", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name="telegram_user_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "telegram_conversation",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "persona", sa.VARCHAR(length=50), autoincrement=False, nullable=False
        ),
        sa.Column(
            "system_prompt",
            sa.VARCHAR(length=100000),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "total_tokens",
            sa.INTEGER(),
            server_default=sa.text("0"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_date",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["telegram_user.id"], name="telegram_conversation_user_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="telegram_conversation_pkey"),
    )
    op.create_table(
        "telegram_ask",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "question", sa.VARCHAR(length=100000), autoincrement=False, nullable=False
        ),
        sa.Column(
            "answer", sa.VARCHAR(length=100000), autoincrement=False, nullable=False
        ),
        sa.Column("token_usage", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["telegram_user.id"], name="telegram_ask_user_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="telegram_ask_pkey"),
    )
    # ### end Alembic commands ###