from typing import List, Annotated
from datetime import date
from fastapi.responses import FileResponse
from app.routers.api_v1.UserStat.schemas import Platform
from fastapi import APIRouter, Depends, Query
from app.routers.api_v1.Auth.dependencies import is_admin_user
from app.routers.api_v1.Overview.schemas import (
    ChatSessionCount,
    TotalTokenCount,
    UserCount,
    ChatMessageCount,
)

from app.routers.api_v1.PersonaStat.schemas import (
    OrderBy,
    PersonaStat,
    PersonaStatRequest,
    PersonaStatTotalResponse,
)
from app.routers.api_v1.PersonaStat.service import (
    export_to_excel_service,
    get_chat_session_counts_service,
    get_persona_users_service,
    get_personas_service,
    get_message_counts_service,
    get_total_tokens_service,
    search_personas_service,
    persona_daily_stat_service,
)
from app.routers.api_v1.Service.schemas import Paginate


from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db


persona_stat_router = APIRouter(
    prefix="/stats/persona",
    tags=["Persona Statistics"],
    responses={404: {"description": "Not found"}},
)


@persona_stat_router.get(
    "/get_personas",
    response_model=Paginate[PersonaStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_personas(
    start_date: date,
    end_date: date,
    limit: int = 10,
    offset: int = 0,
    platform: Platform = Platform.ALL,
    order_by: OrderBy = OrderBy.PERSONA_NAME_ASC,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_personas_service(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        order_by=order_by,
        db_session=db_session,
        platform=platform,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@persona_stat_router.get(
    "/search_personas",
    response_model=Paginate[PersonaStat],
    dependencies=[Depends(is_admin_user)],
)
async def search_personas(
    start_date: date,
    end_date: date,
    limit: int = 10,
    offset: int = 0,
    search_query: Annotated[str, Query()] = "",
    platform: Platform = Platform.ALL,
    order_by: OrderBy = OrderBy.PERSONA_NAME_ASC,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await search_personas_service(
        search_query=search_query,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        order_by=order_by,
        db_session=db_session,
        platform=platform,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@persona_stat_router.post(
    "/persona_daily_stats",
    response_model=PersonaStatTotalResponse,
    dependencies=[Depends(is_admin_user)],
)
async def persona_daily_stats(
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await persona_daily_stat_service(
        persona_stat_request=persona_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@persona_stat_router.post(
    "/get_daily_users",
    response_model=List[UserCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_persona_users(
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_persona_users_service(
        persona_stat_request=persona_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@persona_stat_router.post(
    "/get_daily_messages",
    response_model=List[ChatMessageCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_persona_users(
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_message_counts_service(
        persona_stat_request=persona_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@persona_stat_router.post(
    "/get_daily_total_tokens",
    response_model=List[TotalTokenCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_daily_total_tokens(
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_total_tokens_service(
        persona_stat_request=persona_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@persona_stat_router.post(
    "/get_daily_chat_session_counts",
    response_model=List[ChatSessionCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_daily_chat_session_counts(
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_chat_session_counts_service(
        persona_stat_request=persona_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@persona_stat_router.get(
    "/export_to_excel",
    dependencies=[Depends(is_admin_user)],
)
async def export_to_excel(
    start_date: date,
    end_date: date,
    platform: Platform = Platform.ALL,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    temp_file_name = await export_to_excel_service(
        start_date=start_date,
        end_date=end_date,
        db_session=db_session,
        platform=platform,
        include_developers=include_developers,
        include_archived=include_archived,
    )

    # Return the temporary Excel file using FileResponse
    return FileResponse(
        temp_file_name,
        filename="persona_stat.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
