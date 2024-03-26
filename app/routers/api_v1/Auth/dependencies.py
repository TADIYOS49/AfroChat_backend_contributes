from typing import Annotated
from typing import Any
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import Depends, Body
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.routers.api_v1.Auth.constants import SECRET_KEY
from app.routers.api_v1.Auth.models import Role, User
from app.routers.api_v1.Auth.utils import has_time_passed
from .exceptions import (
    TOKEN_EXPIRED,
    TOO_MANY_CHAT_REQUESTS,
    TOO_MANY_IMAGE_REQUESTS,
    TOO_MANY_PERSONAS_CREATED,
    USER_NOT_ACTIVATED,
    UN_AUTHORIZED_ACCESS_ADMIN,
    USER_NOT_FOUND,
)
from config import initial_config as config

oauth2_schema = OAuth2PasswordBearer(tokenUrl="./api_v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)],
    db_session: AsyncSession = Depends(get_db),
):
    try:
        print("***" * 100)
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY)
        if has_time_passed(payload["exp"]):
            raise TOKEN_EXPIRED

        user: User | None = await User.find(
            db_session=db_session, user_id=UUID(hex=payload["id"])
        )

        if not user:
            raise USER_NOT_FOUND

        return user
    except Exception:
        raise


def get_activated_user(user: User = Depends(get_current_user)):
    if user.is_activated:
        return user
    raise USER_NOT_ACTIVATED


async def get_request_number_validated_user(
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
):
    # calculate the timestamp 1 day before now
    date = datetime.utcnow() - timedelta(days=1)

    chat_count_query = f"""
        select count(cm.id)
        from chat_message cm
        join chat_session cs on cs.id = cm.chat_session_id
        where cs.user_id = '{user.id}' and cm.timestamp > '{date}'
    """

    ask_count_query = f"""
        select count(am.id)
        from ask_message am
        join ask_session ass on ass.id = am.ask_session_id
        where ass.user_id = '{user.id}' and am.created_at > '{date}'
    """

    image_count_query = f"""
        select count(cm.id)
        from chat_message cm
        join chat_session cs on cs.id = cm.chat_session_id
        where cs.user_id = '{user.id}' and cm.timestamp > '{date}' and cm.llm_model = 'DALL-E 3'
    """

    chat_res = await db_session.execute(text(chat_count_query))
    ask_res = await db_session.execute(text(ask_count_query))
    image_res = await db_session.execute(text(image_count_query))

    total_messages_count = chat_res.scalar() + ask_res.scalar()
    dall_e_count = image_res.scalar()

    if total_messages_count > config.MAX_REQUESTS_PER_DAY:
        raise TOO_MANY_CHAT_REQUESTS

    if dall_e_count > config.MAX_DALL_E_REQUESTS_PER_DAY:
        raise TOO_MANY_IMAGE_REQUESTS

    return user


async def get_persona_number_validated_user(
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
):
    # calculate the timestamp 1 day before now
    date = datetime.utcnow() - timedelta(days=1)

    persona_count_query = f"""
        select count(p.id)
        from persona p
        where p.creator_uuid = '{user.id}' and p.created_at > '{date}' 
    """
    persona_res = await db_session.execute(text(persona_count_query))

    if persona_res.scalar() > config.MAX_PERSONA_CREATION_PER_DAY:
        raise TOO_MANY_PERSONAS_CREATED

    return user


def is_admin_user(user: User = Depends(get_activated_user)):
    if user.role >= Role.ADMIN.value:
        return user
    raise UN_AUTHORIZED_ACCESS_ADMIN


def is_super_admin(user: User = Depends(get_activated_user)):
    if user.role >= Role.SUPER_ADMIN.value:
        return user
    raise UN_AUTHORIZED_ACCESS_ADMIN


async def verify_reset_token(
    reset_token: Annotated[str, Body(..., embed=True)],
    db_session: AsyncSession = Depends(get_db),
):
    payload: dict[str, Any] = jwt.decode(reset_token, SECRET_KEY)
    if has_time_passed(payload["exp"]):
        raise TOKEN_EXPIRED

    user: User | None = await User.find(
        db_session=db_session, user_id=UUID(hex=payload["id"])
    )
    if not user:
        raise USER_NOT_FOUND

    return user
