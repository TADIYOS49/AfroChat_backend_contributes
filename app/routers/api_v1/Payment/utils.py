import uuid
from aiogram.bot.api import aiohttp

import ujson

from app.routers.api_v1.Payment.exceptions import SERIVCE_NOT_AVAILABLE
from app.routers.api_v1.Payment.schemas import ChapaResponse
from config import initial_config


"""
chapa response
{'message': 'Hosted Link', 'status': 'success', 'data': {'checkout_url': 'https://checkout.chapa.co/checkout/payment/PN07xSG38ve9zw4JFZRuf3RGx15JR3JI8BBU9b5eFvUgj'}}
"""


async def initiate_chapa_payment(
    amount: float,
    currency: str,
    tx_ref: uuid.UUID,
    description: str,
    title: str,
) -> ChapaResponse:
    payload = ujson.dumps(
        {
            "amount": amount,
            "currency": currency,
            "tx_ref": tx_ref.hex,
            "customization[title]": title,
            "customization[description]": description,
            "customization[logo]": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_light_color_272x92dp.png",
        }
    )
    headers = {
        "Authorization": f"Bearer {initial_config.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                initial_config.CHAPA_URL,
                data=payload,
                headers=headers,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "success":
                        return ChapaResponse(**data)
                raise Exception(
                    f"Request failed with status code {response.status}\
                    error : {await response.text()}",
                )
    except Exception:
        # Handle the exception here other exceptions here
        raise SERIVCE_NOT_AVAILABLE
