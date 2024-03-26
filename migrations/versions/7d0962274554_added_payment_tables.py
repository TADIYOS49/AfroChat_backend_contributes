"""added payment tables

Revision ID: 7d0962274554
Revises: 637ad796cb9a
Create Date: 2024-01-20 00:41:12.221857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7d0962274554"
down_revision = "637ad796cb9a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "subscription_plans",
        sa.Column("plan_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=250), nullable=False),
        sa.Column("description", sa.String(length=250), nullable=False),
        sa.Column("amount", sa.FLOAT(), nullable=False),
        sa.Column("duration_in_days", sa.INTEGER(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "is_active", sa.BOOLEAN(), server_default=sa.text("false"), nullable=False
        ),
        sa.PrimaryKeyConstraint("plan_id"),
    )
    op.create_index(
        op.f("ix_subscription_plans_plan_id"),
        "subscription_plans",
        ["plan_id"],
        unique=True,
    )
    op.create_table(
        "payments",
        sa.Column("payment_id", sa.UUID(), nullable=False),
        sa.Column("plan_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("service_provider", sa.String(length=100), nullable=False),
        sa.Column("payment_status", sa.String(length=100), nullable=False),
        sa.Column("payment_url", sa.String(length=1000), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["subscription_plans.plan_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("payment_id", "plan_id", "user_id"),
    )
    op.create_index(
        op.f("ix_payments_payment_id"), "payments", ["payment_id"], unique=True
    )
    op.create_table(
        "customer_subscriptions",
        sa.Column("subscription_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("payment_id", sa.UUID(), nullable=False),
        sa.Column(
            "start_date", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["payment_id"],
            ["payments.payment_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("subscription_id", "user_id", "payment_id"),
        sa.UniqueConstraint("payment_id"),
    )
    op.create_index(
        op.f("ix_customer_subscriptions_subscription_id"),
        "customer_subscriptions",
        ["subscription_id"],
        unique=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_customer_subscriptions_subscription_id"),
        table_name="customer_subscriptions",
    )
    op.drop_table("customer_subscriptions")
    op.drop_index(op.f("ix_payments_payment_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_index(
        op.f("ix_subscription_plans_plan_id"), table_name="subscription_plans"
    )
    op.drop_table("subscription_plans")
    # ### end Alembic commands ###