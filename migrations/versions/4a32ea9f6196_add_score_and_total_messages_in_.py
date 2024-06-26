"""Add score and total messages in personas ans subtools

Revision ID: 4a32ea9f6196
Revises: ecf1ef0c6edb
Create Date: 2024-02-23 08:49:54.118289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4a32ea9f6196"
down_revision = "ecf1ef0c6edb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "persona", sa.Column("score", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "persona",
        sa.Column("total_messages", sa.Integer(), server_default="0", nullable=False),
    )
    op.drop_column("persona", "rank")
    op.add_column(
        "sub_tool", sa.Column("score", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "sub_tool",
        sa.Column("total_messages", sa.Integer(), server_default="0", nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("sub_tool", "total_messages")
    op.drop_column("sub_tool", "score")
    op.add_column(
        "persona",
        sa.Column(
            "rank",
            sa.INTEGER(),
            server_default=sa.text("0"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("persona", "total_messages")
    op.drop_column("persona", "score")
    # ### end Alembic commands ###
