from typing import List
from datetime import date, datetime
from app.routers.api_v1.ExtraStat.schemas import (
    AverageInfo,
    DailySignedUpUsers,
    PersonaStat,
    SubToolStat,
    ToolStat,
)
from app.routers.api_v1.ExtraStat.service import (
    get_average_info_service,
    get_daily_signed_up_users_service,
    get_personas_service,
    get_sub_tools_service,
    get_tools_service,
)
from app.routers.api_v1.Overview.constants import START_DATE
from fastapi import APIRouter, Depends
from app.routers.api_v1.Auth.dependencies import is_admin_user

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db


extra_stat_router = APIRouter(
    prefix="/stats/extra",
    tags=["Extra Statistics"],
    responses={404: {"description": "Not found"}},
)


@extra_stat_router.get(
    "/get_personas",
    response_model=List[PersonaStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_personas(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_personas_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )


@extra_stat_router.get(
    "/get_sub_tools",
    response_model=List[SubToolStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_sub_tools(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_sub_tools_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )


@extra_stat_router.get(
    "/get_tools",
    response_model=List[ToolStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_tools(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_tools_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )


@extra_stat_router.get(
    "/get_average_info",
    response_model=AverageInfo,
    dependencies=[Depends(is_admin_user)],
)
async def get_tools(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_average_info_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )


@extra_stat_router.get(
    "/get_daily_signed_up_users",
    response_model=List[DailySignedUpUsers],
    dependencies=[Depends(is_admin_user)],
)
async def get_daily_signed_up_users(
    start_date: date = START_DATE,
    end_date: date = datetime.now().date(),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_daily_signed_up_users_service(
        start_date=start_date, end_date=end_date, db_session=db_session
    )
