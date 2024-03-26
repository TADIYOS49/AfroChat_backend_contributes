from datetime import datetime, timedelta
import uuid
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.routers.api_v1.Auth.models import User
from app.routers.api_v1.Payment.exceptions import (
    PAYMENT_NOT_FOUND,
    SUBSCRIPTION_PLAN_NOT_FOUND,
)
from app.routers.api_v1.Payment.models import (
    CustomerSubscription,
    PaymentGateways,
    Payments,
    SubscriptionPlan,
    TransactionStatus,
)
from app.routers.api_v1.Payment.schemas import (
    ChapaResponse,
    SubscriptionPlanModel,
    SubscriptionPlanUpdate,
)
from app.routers.api_v1.Payment.utils import initiate_chapa_payment


async def create_new_subscription_plan(
    db_session: AsyncSession, plan: SubscriptionPlanModel
):
    # save to db
    plan_db = SubscriptionPlan(
        **plan.model_dump(), is_active=True, created_at=datetime.utcnow()
    )
    try:
        db_session.add(plan_db)
        await db_session.commit()
        return plan_db
    except SQLAlchemyError as e:
        # add logger here
        await db_session.rollback()
        raise e


async def get_all_subscription_plans(
    db_session: AsyncSession,
) -> list[SubscriptionPlan]:
    try:
        plans = await db_session.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.is_active)
        )
        results: list[SubscriptionPlan] = list(plans.scalars().all())
        return results
    except SQLAlchemyError as e:
        # add logger here
        await db_session.rollback()
        raise e


async def get_subscription_plan_by_id(
    db_session: AsyncSession, plan_id: uuid.UUID
) -> SubscriptionPlan:
    try:
        plan = await db_session.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.plan_id == plan_id)
        )
        result: SubscriptionPlan | None = plan.scalars().first()
        if not result:
            raise SUBSCRIPTION_PLAN_NOT_FOUND
        return result
    except SQLAlchemyError as e:
        # add logger here
        await db_session.rollback()
        raise e


async def delete_subscription_plan_by_id_soft(
    db_session: AsyncSession, plan_id: uuid.UUID
) -> bool:
    try:
        query = (
            update(SubscriptionPlan)
            .where(
                SubscriptionPlan.plan_id == plan_id,
                SubscriptionPlan.is_active,
            )
            .values(is_active=False)
        )

        affected_rows = await db_session.execute(query)
        await db_session.commit()
        if affected_rows.rowcount == 0:
            raise SUBSCRIPTION_PLAN_NOT_FOUND
        return True
    except SQLAlchemyError as e:
        # add logger here
        await db_session.rollback()
        raise e


async def delete_subscription_plan_by_id_hard(
    db_session: AsyncSession, plan_id: uuid.UUID
) -> bool:
    # have to be an admin
    try:
        query = delete(SubscriptionPlan).where(
            SubscriptionPlan.plan_id == plan_id,
        )
        affected_rows = await db_session.execute(query)
        await db_session.commit()
        if affected_rows.rowcount == 0:
            raise SUBSCRIPTION_PLAN_NOT_FOUND
        return True
    except SQLAlchemyError as e:
        # add logger here
        await db_session.rollback()
        raise e


async def update_plan_by_id(
    db_session: AsyncSession, plan: SubscriptionPlanUpdate
) -> bool:
    try:
        query = (
            update(SubscriptionPlan)
            .where(SubscriptionPlan.plan_id == plan.plan_id)
            .values(**plan.model_dump(exclude={"plan_id"}, exclude_unset=True))
        )
        affected_rows = await db_session.execute(query)
        await db_session.commit()
        if affected_rows.rowcount == 0:
            raise SUBSCRIPTION_PLAN_NOT_FOUND
        return True
    except SQLAlchemyError as e:
        # add logger here
        await db_session.rollback()
        raise e


async def get_payment_by_id(
    db_session: AsyncSession, payment_id: uuid.UUID
) -> Payments:
    query = (
        select(Payments)
        .options(selectinload(Payments.plan))
        .where(Payments.payment_id == payment_id)
    )
    result = await db_session.execute(query)
    result = result.scalars().first()
    if not result:
        raise PAYMENT_NOT_FOUND

    return result


async def process_payment(
    db_session: AsyncSession,
    plan_id: uuid.UUID,
    user: User,
    payment_gateway: PaymentGateways,
) -> Payments:
    if payment_gateway == PaymentGateways.CHAPA:
        return await process_chapa_payment(
            db_session=db_session,
            plan_id=plan_id,
            user=user,
            payment_gateway=payment_gateway,
        )
    # TODO : add other payment gateways here
    return Payments()


async def process_chapa_payment(
    db_session: AsyncSession,
    plan_id: uuid.UUID,
    user: User,
    payment_gateway: PaymentGateways,
) -> Payments:
    plan = await get_subscription_plan_by_id(db_session=db_session, plan_id=plan_id)
    print("-----" * 100)
    print("got here", plan)
    new_transaction_id = uuid.uuid4()
    response: ChapaResponse = await initiate_chapa_payment(
        amount=plan.amount,
        currency="ETB",
        tx_ref=new_transaction_id,
        description=plan.description,
        title=plan.name,
    )
    print(response)
    # create a new database instance
    db_payment = Payments(
        payment_id=new_transaction_id,
        plan_id=plan_id,
        user_id=user.id,
        service_provider=payment_gateway.value,
        payment_status=TransactionStatus.Pending.value,
        payment_url=response.data.checkout_url,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(db_payment)
        await db_session.commit()
        return db_payment
    except SQLAlchemyError as e:
        # add logger here
        await db_session.rollback()
        raise e


async def add_subscription(
    db_session: AsyncSession,
    tx_ref: uuid.UUID,
):
    payment = await get_payment_by_id(db_session=db_session, payment_id=tx_ref)
    if payment.payment_status == TransactionStatus.Completed.value:
        # payment already processed
        return
    payment.updated_at = datetime.utcnow()
    payment.payment_status = TransactionStatus.Completed.value

    db_subscription = CustomerSubscription(
        subscription_id=uuid.uuid4(),
        user_id=payment.user_id,
        payment_id=payment.payment_id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=payment.plan.duration_in_days),
        created_at=datetime.utcnow(),
    )
    try:
        db_session.add(db_subscription)
        await db_session.commit()
        return db_subscription
    except SQLAlchemyError as e:
        # add logger here
        await db_session.rollback()
        raise e
