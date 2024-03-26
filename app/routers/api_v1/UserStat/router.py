from typing import List, Annotated
from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from app.routers.api_v1.Service.schemas import Paginate
from app.routers.api_v1.chat.schemas import ChatMessageOutSchema, ChatSessionBase
from fastapi import APIRouter, Depends
from app.routers.api_v1.Auth.dependencies import is_admin_user
from app.routers.api_v1.Overview.schemas import (
    ChatSessionCount,
    TotalTokenCount,
    ChatMessageCount,
)

from app.routers.api_v1.UserStat.schemas import (
    ChatSummaryOut,
    IndividualRequest,
    IndividualStatRequest,
    IndividualUserDailyStat,
    OrderBy,
    Platform,
    UserChatSessionRequest,
    UserDailyStat,
    UserPersonaStat,
    UserPersonaStatRequest,
    UserStat,
    UserStatRequest,
    UserStatResponse,
    UserStatTotalResponse,
    UserSubToolStat,
    UserSubToolStatRequest,
    UserToolStat,
)
from app.routers.api_v1.UserStat.service import (
    export_to_excel_service,
    get_chat_messages_service,
    get_chat_session_counts_service,
    get_chat_summary_service,
    get_engaged_personas_service,
    get_engaged_sub_tools_service,
    get_engaged_tools_service,
    get_individual_user_stat_service,
    get_persona_chat_sessions_service,
    get_sub_tool_chat_sessions_service,
    get_user_stat_service,
    get_users_service,
    get_message_counts_service,
    get_total_tokens_service,
    search_users_service,
    user_daily_stat_service,
)


from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db


user_stat_router = APIRouter(
    prefix="/stats/user",
    tags=["User Statistics"],
    responses={404: {"description": "Not found"}},
)


@user_stat_router.get(
    "/get_users",
    response_model=Paginate[UserStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_users(
    start_date: date,
    end_date: date,
    limit: int = 10,
    offset: int = 0,
    platform: Annotated[Platform, Query()] = Platform.ALL,
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
    order_by: OrderBy = Query(OrderBy.USERNAME_ASC, alias="order_by"),
    db_session: AsyncSession = Depends(get_db),
):
    return await get_users_service(
        include_developers=include_developers,
        include_archived=include_archived,
        platform=platform,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        order_by=order_by,
        db_session=db_session,
    )


@user_stat_router.get(
    "/search_users",
    response_model=Paginate[UserStat],
    dependencies=[Depends(is_admin_user)],
)
async def search_users(
    start_date: date,
    end_date: date,
    limit: int = 10,
    offset: int = 0,
    search_query: Annotated[str, Query()] = "",
    include_developers: Annotated[bool, Query()] = False,
    include_archived: Annotated[bool, Query()] = False,
    platform: Platform = Platform.ALL,
    order_by: OrderBy = OrderBy.USERNAME_ASC,
    db_session: AsyncSession = Depends(get_db),
):
    return await search_users_service(
        search_query=search_query,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        include_developers=include_developers,
        include_archived=include_archived,
        platform=platform,
        order_by=order_by,
        db_session=db_session,
    )


@user_stat_router.post(
    "/get_user_stat",
    response_model=List[UserDailyStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_user_stat(
    user_stat_request: UserStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_user_stat_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/user_daily_stat",
    response_model=UserStatTotalResponse,
    dependencies=[Depends(is_admin_user)],
)
async def user_daily_stat(
    user_stat_request: UserStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await user_daily_stat_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_individual_user_stat",
    response_model=List[IndividualUserDailyStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_individual_user_stat(
    user_stat_request: IndividualStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_individual_user_stat_service(
        user_stat_request=user_stat_request.data, db_session=db_session
    )


@user_stat_router.post(
    "/get_persona_chat_sessions",
    response_model=List[ChatSessionBase],
    dependencies=[Depends(is_admin_user)],
)
async def get_persona_chat_sessions(
    user_stat_request: UserPersonaStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_persona_chat_sessions_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_sub_tool_chat_sessions",
    response_model=List[ChatSessionBase],
    dependencies=[Depends(is_admin_user)],
)
async def get_sub_tool_chat_sessions(
    user_stat_request: UserSubToolStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_sub_tool_chat_sessions_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_chat_messages",
    response_model=List[ChatMessageOutSchema],
    dependencies=[Depends(is_admin_user)],
)
async def get_chat_messages(
    user_stat_request: UserChatSessionRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_chat_messages_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_chat_summary",
    response_model=ChatSummaryOut,
    dependencies=[Depends(is_admin_user)],
)
async def get_chat_summary(
    user_stat_request: UserChatSessionRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_chat_summary_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_engaged_personas",
    response_model=List[UserPersonaStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_engaged_personas(
    user_stat_request: UserStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_engaged_personas_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_engaged_sub_tools",
    response_model=List[UserSubToolStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_engaged_sub_tools(
    user_stat_request: UserStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_engaged_sub_tools_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_engaged_tools",
    response_model=List[UserToolStat],
    dependencies=[Depends(is_admin_user)],
)
async def get_engaged_tools(
    user_stat_request: UserStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_engaged_tools_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_daily_messages",
    response_model=List[ChatMessageCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_user_users(
    user_stat_request: UserStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_message_counts_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_daily_total_tokens",
    response_model=List[TotalTokenCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_daily_total_tokens(
    user_stat_request: UserStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_total_tokens_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.post(
    "/get_daily_chat_session_counts",
    response_model=List[ChatSessionCount],
    dependencies=[Depends(is_admin_user)],
)
async def get_daily_chat_session_counts(
    user_stat_request: UserStatRequest,
    db_session: AsyncSession = Depends(get_db),
):
    return await get_chat_session_counts_service(
        user_stat_request=user_stat_request, db_session=db_session
    )


@user_stat_router.get(
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
        filename="user_stat.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
