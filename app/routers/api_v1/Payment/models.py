"""
CREATE TABLE subscription_plans (
    plan_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    Description VARCHAR(250) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    duration_in_days INT NOT NULL
    -- Add more details if needed (e.g., features, description)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
"""
from datetime import datetime
from enum import Enum
from uuid import UUID
import uuid
from pydantic_core import Url
from sqlalchemy import BOOLEAN, FLOAT, INTEGER, ForeignKey, false, func

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as sqlalchemy_UUID
from sqlalchemy import String
from app.database.base import Base
from app.routers.api_v1.Payment.constants import CurrentFeatures, CurrentGateways


class TransactionStatus(Enum):
    Pending = "pending"
    Completed = "Done"


class SupportedPaymentGateways:
    def __init__(self, name: str, image_url: Url) -> None:
        self.name = name
        self.image_url = image_url


class PremiumFeatures:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description


Features: list[PremiumFeatures] = [
    PremiumFeatures(feature, "") for feature in CurrentFeatures
]


Gateways = [
    SupportedPaymentGateways(gateway["name"], Url(gateway["logo"]))
    for gateway in CurrentGateways
]


class PaymentGateways(Enum):
    CHAPA = "Chapa"


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    plan_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    amount: Mapped[float] = mapped_column(FLOAT, nullable=False)

    duration_in_days: Mapped[int] = mapped_column(INTEGER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        BOOLEAN, server_default=false(), nullable=False
    )

    payments: Mapped[list["Payments"]] = relationship(
        "Payments",
        back_populates="plan",
    )


class Payments(Base):
    """
    if it's telebirr then my transaction_id could be trader_out No.
    if it's chapa then my transaction_id could be chapa tf_rex.
    the implementation to use this payment get way will be different in most use cases.
    """

    __tablename__ = "payments"

    payment_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    plan_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("subscription_plans.plan_id"),
        primary_key=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True
    )

    service_provider: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan", back_populates="payments"
    )


class CustomerSubscription(Base):
    __tablename__ = "customer_subscriptions"
    subscription_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    # for simpler queries
    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
        primary_key=True,
    )

    payment_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("payments.payment_id"),
        primary_key=True,
        unique=True,  # insures one payment only persists here
    )

    start_date: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    end_date: Mapped[datetime] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
