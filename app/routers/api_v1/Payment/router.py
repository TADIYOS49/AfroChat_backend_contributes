import hmac
from typing import Annotated
from cloudinary.utils import hashlib
from fastapi import APIRouter, Body, Depends, Request
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import ujson
from app.database.database import get_db
from app.routers.api_v1.Auth.dependencies import get_activated_user, is_admin_user
from app.routers.api_v1.Auth.models import User
from app.routers.api_v1.Payment.constants import CHAPA_SECRET_HASH
from app.routers.api_v1.Payment.models import (
    Features,
    Gateways,
    PaymentGateways,
)
from app.routers.api_v1.Payment.schemas import (
    PaymentGatewaysSchema,
    PaymentOut,
    PremiumFeaturesSchema,
    SubscriptionPlanModel,
    SubscriptionPlanOut,
    SubscriptionPlanUpdate,
)

from app.routers.api_v1.Payment.service import (
    add_subscription,
    create_new_subscription_plan,
    delete_subscription_plan_by_id_hard,
    delete_subscription_plan_by_id_soft,
    get_all_subscription_plans,
    get_subscription_plan_by_id,
    process_payment,
    update_plan_by_id,
)

payment_router = APIRouter(prefix="/payment", tags=["Payment"])


@payment_router.post(
    "/create-plan",
    response_model=SubscriptionPlanOut,
    description="Create a new subscription plan",
    dependencies=[Depends(is_admin_user)],
)
async def create_plan(
    plan: SubscriptionPlanModel,
    db_session: AsyncSession = Depends(get_db),
):
    return await create_new_subscription_plan(db_session=db_session, plan=plan)


@payment_router.get(
    "/get-all-plans",
    response_model=list[SubscriptionPlanOut],
    description="Get all subscription plans",
    dependencies=[Depends(get_activated_user)],
)
async def get_all_palns(db_session: AsyncSession = Depends(get_db)):
    return await get_all_subscription_plans(db_session=db_session)


@payment_router.get(
    "/get-plan",
    response_model=SubscriptionPlanOut,
    description="Get one subscription plans by plan id",
    dependencies=[Depends(get_activated_user)],
)
async def get_one_plan(
    plan_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_subscription_plan_by_id(db_session=db_session, plan_id=plan_id)


# soft delete plan
@payment_router.delete(
    "/delete-subscription-plan-soft",
    description="Delete one subscription plans by plan id this will\
            just change the plan from active to inactive",
    dependencies=[Depends(is_admin_user)],
)
async def delete_subscription_plan_soft(
    plan_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
):
    await delete_subscription_plan_by_id_soft(db_session=db_session, plan_id=plan_id)
    return {"message": "plan deleted successfully"}


# hard delete plan
@payment_router.delete(
    "/delete-subscription-plan-hard",
    description="Delete one subscription plans by plan id this will delete the plan permanently",
    dependencies=[Depends(is_admin_user)],
)
async def delete_subscription_plan_hard(
    plan_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
):
    await delete_subscription_plan_by_id_hard(db_session=db_session, plan_id=plan_id)
    return {"message": "plan deleted successfully"}


@payment_router.put(
    "/update-subscription-plan",
    description="Update one subscription plans by plan id returns the payload that have been sent",
    response_model=SubscriptionPlanUpdate,
    dependencies=[Depends(is_admin_user)],
)
async def update_subscription_plan(
    plan: SubscriptionPlanUpdate,
    db_session: AsyncSession = Depends(get_db),
):
    await update_plan_by_id(db_session=db_session, plan=plan)
    return plan


@payment_router.post(
    "/make-payment",
    description="Make a payment user have to send the payment_id, and the type of service provide for the payment to continue forward",
    response_model=PaymentOut,
)
async def make_payment(
    payment_gateway: Annotated[PaymentGateways, Body()],
    subscription_plan_id: Annotated[uuid.UUID, Body()],
    user: Annotated[User, Depends(get_activated_user)],
    db_session: AsyncSession = Depends(get_db),
):
    return await process_payment(
        db_session=db_session,
        plan_id=subscription_plan_id,
        user=user,
        payment_gateway=payment_gateway,
    )


@payment_router.post(
    "/chapa-notification-webhook",
    description="when payments are done this end point will be triggered",
)
async def payment_webhook(
    req: Request,
    db_session: AsyncSession = Depends(get_db),
):
    json_body = await req.json()
    headers = req.headers

    hmac_obj = hmac.new(
        CHAPA_SECRET_HASH.encode("utf-8"),
        ujson.dumps(json_body).encode("utf-8"),
        hashlib.sha256,
    )
    if hmac_obj.hexdigest() == headers["x-chapa-signature"]:
        await add_subscription(
            db_session=db_session, tx_ref=uuid.UUID(json_body["tx_ref"])
        )
        return {"message": "payment successful"}


@payment_router.get(
    "/get_payment_gateways",
    response_model=list[PaymentGatewaysSchema],
    dependencies=[Depends(get_activated_user)],
)
async def get_payment_gateways():
    return Gateways


@payment_router.get(
    "/get_premium_features",
    response_model=list[PremiumFeaturesSchema],
)
async def get_premium_features():
    return Features
