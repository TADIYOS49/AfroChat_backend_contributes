from typing import List, Annotated
from datetime import date
from app.routers.api_v1.Service.schemas import Paginate
from app.routers.api_v1.UserStat.schemas import Platform

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from app.routers.api_v1.Auth.dependencies import is_admin_user
from app.routers.api_v1.Overview.schemas import (
    ChatSessionCount,
    TotalTokenCount,
    UserCount,
    ChatMessageCount,
)

from app.routers.api_v1.ToolStat.schemas import (
    OrderBy,
    ToolStat,
    ToolStatRequest,
    ToolStatTotalResponse,
)
from app.routers.api_v1.ToolStat.service import (
    export_to_excel_service,
    get_chat_session_counts_service,
    get_tool_users_service,
    get_tools_service,
    get_message_counts_service,
    get_total_tokens_service,
    search_tools_service,
    tool_daily_stat_service,
)


from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db


tool_stat_router = APIRouter(
    prefix="/stats/tool",
    tags=["Tool Statistics"],
    responses={404: {"description": "Not found"}},
)


@tool_stat_router.get(
    "/get_tools",
    response_model=Paginate[ToolStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_tools(
    start_date: date,
    end_date: date,
    limit: int = 10,
    offset: int = 0,
    platform: Platform = Platform.ALL,
    order_by: OrderBy = OrderBy.TOOL_NAME_ASC,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_tools_service(
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


@tool_stat_router.get(
    "/search_tools",
    response_model=Paginate[ToolStat],
    dependencies=[Depends(is_admin_user)],
)
async def search_tools(
    start_date: date,
    end_date: date,
    limit: int = 10,
    offset: int = 0,
    search_query: Annotated[str, Query()] = "",
    platform: Platform = Platform.ALL,
    order_by: OrderBy = OrderBy.TOOL_NAME_ASC,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await search_tools_service(
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


@tool_stat_router.post(
    "/tool_daily_stat",
    response_model=ToolStatTotalResponse,
    dependencies=[Depends(is_admin_user)],
)
async def tool_daily_stat(
    tool_stat_request: ToolStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await tool_daily_stat_service(
        tool_stat_request=tool_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@tool_stat_router.post(
    "/get_daily_users",
    response_model=List[UserCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_tool_users(
    tool_stat_request: ToolStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_tool_users_service(
        tool_stat_request=tool_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@tool_stat_router.post(
    "/get_daily_messages",
    response_model=List[ChatMessageCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_tool_users(
    tool_stat_request: ToolStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_message_counts_service(
        tool_stat_request=tool_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@tool_stat_router.post(
    "/get_daily_total_tokens",
    response_model=List[TotalTokenCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_daily_total_tokens(
    tool_stat_request: ToolStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_total_tokens_service(
        tool_stat_request=tool_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@tool_stat_router.post(
    "/get_daily_chat_session_counts",
    response_model=List[ChatSessionCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_daily_chat_session_counts(
    tool_stat_request: ToolStatRequest,
    db_session: AsyncSession = Depends(get_db),
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
):
    return await get_chat_session_counts_service(
        tool_stat_request=tool_stat_request,
        db_session=db_session,
        include_developers=include_developers,
        include_archived=include_archived,
    )


@tool_stat_router.get(
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
        filename="tool_stat.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
