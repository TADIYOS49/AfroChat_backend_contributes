from datetime import date, datetime
from typing import List
from app.routers.api_v1.Overview.constants import START_DATE
from fastapi import APIRouter, Depends
from app.routers.api_v1.Auth.dependencies import is_admin_user
from app.routers.api_v1.Overview.schemas import (
    ChatMessageCount,
    ChatSessionCount,
    TotalTokenCount,
    UserCount,
    OverviewInfo,
)
from app.routers.api_v1.Overview.service import (
    get_active_user_counts_service,
    get_chat_session_counts_service,
    get_message_counts_service,
    get_overview_info_service,
    get_total_tokens_service,
)


from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db


overview_router = APIRouter(
    prefix="/overview",
    tags=["Overview"],
    responses={404: {"description": "Not found"}},
)


@overview_router.get(
    "/get_info",
    response_model=OverviewInfo,
    dependencies=[Depends(is_admin_user)],
)
async def get_overview_info(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_overview_info_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )


@overview_router.get(
    "/get_active_user_counts",
    response_model=List[UserCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_active_user_counts(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_active_user_counts_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )


@overview_router.get(
    "/get_message_counts",
    response_model=List[ChatMessageCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_message_counts(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_message_counts_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )


@overview_router.get(
    "/get_chat_session_counts",
    response_model=List[ChatSessionCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_chat_session_counts(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_chat_session_counts_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )


@overview_router.get(
    "/get_total_tokens",
    response_model=List[TotalTokenCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_total_tokens(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_total_tokens_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )
