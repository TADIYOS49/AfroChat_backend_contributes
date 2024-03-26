from fastapi import APIRouter
from typing import Annotated
from fastapi import APIRouter, Depends
from app.routers.api_v1.Auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.routers.api_v1.Share.service import deep_copy_chat_session_messages

from app.database import get_db
from app.routers.api_v1.Auth.dependencies import get_activated_user

share_router = APIRouter(
    tags=["Share"],
    responses={404: {"description": "Not found"}},
)


@share_router.post(
    "/share",
    status_code=200,
)
async def share_chat(
    user: Annotated[User, Depends(get_activated_user)],
    chat_session_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    return await deep_copy_chat_session_messages(
        db_session=db_session, chat_session_id=chat_session_id, recipient_id=user.id
    )
