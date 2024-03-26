from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Body, Depends, UploadFile
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.api_v1.chat.service import upload_image_to_cloudinary
from app.database.database import get_db
from app.routers.api_v1.Auth.exceptions import (
    USER_NOT_FOUND,
    InvalidTelegramCredentials,
)
from app.routers.api_v1.Auth.models import User
from app.routers.api_v1.Auth.schemas import TelegramAuthenticationSchema
from app.routers.api_v1.Auth.utils import validate_initData
from app.routers.api_v1.Image.service import (
    edit_image_with_prompt,
    generate_caption_from_image,
    generate_description_from_image,
)
from app.routers.api_v1.Auth.dependencies import get_activated_user
from app.bot import dp

image_router = APIRouter(
    prefix="/image",
    tags=["Image"],
    responses={404: {"description": "Not found"}},
)


@image_router.post("/caption_image", dependencies=[Depends(get_activated_user)])
async def caption_image(
    image: UploadFile,
):
    text = await generate_caption_from_image(image)
    return {"caption": text}


@image_router.post("/send_image")
async def telegram_login(
    telegram_schema: TelegramAuthenticationSchema,
    image_url: Annotated[HttpUrl, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    is_valid, telegram_user = validate_initData(
        telegram_schema.hash_str,
        telegram_schema.initData,
        telegram_schema.telegram_user,
    )

    if not is_valid:
        raise InvalidTelegramCredentials

    telegram_id: str = str(telegram_user.get("id", ""))

    db_user: User | None = await User.find_by_telegram_id(
        db_session=db_session, telegram_id=telegram_id
    )

    if not db_user:
        raise USER_NOT_FOUND

    await dp.bot.send_photo(telegram_id, str(image_url))
    return {"status": "ok"}


@image_router.post("/describe_image", dependencies=[Depends(get_activated_user)])
async def describe_image(
    image_url: str,
):
    text = await generate_description_from_image(image_url)
    return {"description": text}


@image_router.post("/edit_image")
async def edit_image(
    image_url: str,
    prompt: str,
):
    img = await edit_image_with_prompt(image_url=image_url, prompt=prompt)

    timestamp = datetime.utcnow()
    unique_filename = f"{str(111)}_{timestamp}"
    public_id = f"generated_images/{unique_filename}"

    # Upload the generated image to Cloudinary with the specified public_id
    cloudinary_url = upload_image_to_cloudinary(img, public_id)
    return cloudinary_url
