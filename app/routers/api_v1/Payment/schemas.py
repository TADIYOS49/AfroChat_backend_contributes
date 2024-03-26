from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from pydantic_core import Url


class SubscriptionPlanModel(BaseModel):
    name: str = Field(..., min_length=5, max_length=250)
    description: str = Field(..., min_length=5, max_length=250)
    amount: float = Field(gt=0)
    duration_in_days: int = Field(gt=0)


class SubscriptionPlanInDB(SubscriptionPlanModel):
    created_at: datetime
    is_active: bool


class SubscriptionPlanOut(SubscriptionPlanInDB):
    plan_id: UUID


class SubscriptionPlanUpdate(BaseModel):
    plan_id: UUID
    name: str | None = Field(default=None, min_length=5, max_length=250)
    description: str | None = Field(default=None, min_length=5, max_length=250)
    amount: float | None = Field(default=None, gt=0)
    duration_in_days: int | None = Field(default=None, gt=0)


"""
chapa response
{'message': 'Hosted Link', 'status': 'success', 'data': {'checkout_url': 'https://checkout.chapa.co/checkout/payment/PN07xSG38ve9zw4JFZRuf3RGx15JR3JI8BBU9b5eFvUgj'}}
"""


class ChapaUrl(BaseModel):
    checkout_url: str


class ChapaResponse(BaseModel):
    message: str
    status: str
    data: ChapaUrl


class PaymentOut(BaseModel):
    payment_id: UUID
    plan_id: UUID
    user_id: UUID
    service_provider: str
    payment_status: str
    payment_url: str
    created_at: datetime
    updated_at: datetime


class PaymentGatewaysSchema(BaseModel):
    name: str
    image_url: Url


class PremiumFeaturesSchema(BaseModel):
    name: str
    description: str
