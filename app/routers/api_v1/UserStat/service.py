from datetime import date, timedelta
from app.utils.logger import FastApiLogger
import tempfile
from typing import List
from app.constants import LLMModels
import pandas as pd
from app.bot.api_requests import make_request
from app.routers.api_v1.Auth.models import User
from app.routers.api_v1.Overview.schemas import (
    ChatMessageCount,
    ChatSessionCount,
    TotalTokenCount,
)
from app.routers.api_v1.Service.schemas import Meta, Paginate
from app.routers.api_v1.UserStat.schemas import (
    ChatSummaryOut,
    DailyStat,
    DailyUsage,
    IndividualDailyUsage,
    IndividualRequest,
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
from app.routers.api_v1.chat.models import (
    ChatMessage,
    ChatSession,
    SummarizedChatSessionSnapShot,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy import select


async def get_users_service(
    start_date: date,
    end_date: date,
    limit: int,
    offset: int,
    order_by: OrderBy,
    db_session: AsyncSession,
    platform: Platform = Platform.ALL,
    include_developers: bool = False,
    include_archived: bool = False,
):
    platform_filter = ""
    if platform == Platform.TELEGRAM_BOT:
        platform_filter = "AND chat_message.message_from = 1"
    elif platform == Platform.TELEGRAM_MINI_APP:
        platform_filter = "AND chat_message.message_from = 2"
    elif platform == Platform.MOBILE_APP:
        platform_filter = "AND chat_message.message_from = 3"

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            "user".id AS user_id,
            "user".username,
            COALESCE(COUNT(cm.id), 0) AS total_chat_messages,
            COALESCE(SUM(cm.token_usage), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT cm.chat_session_id), 0) AS total_chat_sessions,
            COALESCE(COUNT(DISTINCT persona.id), 0) AS total_personas,
            COALESCE(COUNT(DISTINCT sub_tool.sub_tool_id), 0) AS total_sub_tools,
            COALESCE(COUNT(DISTINCT sub_tool.tool_id), 0) AS total_tools
        FROM
            "user"
        JOIN
            (
                chat_session
                JOIN
                    (
                        SELECT * FROM chat_message
                        WHERE
                            chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                    ) as cm
                    ON chat_session.id = cm.chat_session_id
                LEFT JOIN
                    persona ON chat_session.persona_id = persona.id
                LEFT JOIN
                    sub_tool ON chat_session.sub_tool_id = sub_tool.sub_tool_id
            )
            ON "user".id = chat_session.user_id
        AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
        AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
        GROUP BY
            "user".id, "user".username
        ORDER BY
            {order_by.value}
        OFFSET
            {offset}
        LIMIT
            {limit}
        """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()

    # Define the SQL query
    count_query = text(
        f"""
        SELECT
            COUNT(DISTINCT "user".id) as total_count
        FROM
            "user"
        JOIN
            (
                chat_session
                JOIN
                    (
                        SELECT * FROM chat_message
                        WHERE
                            chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                    ) as cm
                ON cm.chat_session_id = chat_session.id
            )
            ON "user".id = chat_session.user_id
            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
        """
    )

    total_count = (await db_session.execute(count_query)).scalar()

    # Define the SQL query
    max_val_query = text(
        f"""
        SELECT MAX(total_chat_messages) AS max_value
        FROM
            (
                SELECT
                    "user".id AS user_id,
                    COALESCE(COUNT(cm.id), 0) AS total_chat_messages
                FROM
                    "user"
                JOIN
                    (
                        chat_session
                        JOIN
                            (
                                SELECT * FROM chat_message
                                WHERE
                                    chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                            ) as cm
                            ON chat_session.id = cm.chat_session_id
                    )
                    ON "user".id = chat_session.user_id
                    AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
                    AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
                GROUP BY
                    "user".id
            ) AS sub_query
        """
    )

    max_value = (await db_session.execute(max_val_query)).scalar()

    # Perform transformation if a transformer function is provided
    items = [
        UserStat(
            user_id=row.user_id,
            username=row.username,
            total_chat_messages=row.total_chat_messages,
            total_token_usage=row.total_token_usage,
            total_number_of_personas=row.total_personas,
            total_number_of_sub_tools=row.total_sub_tools,
            total_number_of_tools=row.total_tools,
            total_chat_sessions=row.total_chat_sessions,
        )
        for row in rows
    ]

    meta_data: dict[str, int] = {
        "offset": offset,
        "limit": limit,
        "total": total_count,
        "returned": len(items),
        "max_value": max(max_value, 100),
    }

    # Create a Paginate object with metadata and paginated data
    response = Paginate[UserStat](meta_data=Meta(**meta_data), data=items)

    return response


async def search_users_service(
    search_query: str,
    start_date: date,
    end_date: date,
    limit: int,
    offset: int,
    order_by: OrderBy,
    db_session: AsyncSession,
    platform: Platform = Platform.ALL,
    include_developers: bool = False,
    include_archived: bool = False,
):
    platform_filter = ""
    if platform == Platform.TELEGRAM_BOT:
        platform_filter = "AND chat_message.message_from = 1"
    elif platform == Platform.TELEGRAM_MINI_APP:
        platform_filter = "AND chat_message.message_from = 2"
    elif platform == Platform.MOBILE_APP:
        platform_filter = "AND chat_message.message_from = 3"

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            "user".id AS user_id,
            "user".username,
            COALESCE(COUNT(cm.id), 0) AS total_chat_messages,
            COALESCE(SUM(cm.token_usage), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT cm.chat_session_id), 0) AS total_chat_sessions,
            COALESCE(COUNT(DISTINCT persona.id), 0) AS total_personas,
            COALESCE(COUNT(DISTINCT sub_tool.sub_tool_id), 0) AS total_sub_tools,
            COALESCE(COUNT(DISTINCT sub_tool.tool_id), 0) AS total_tools
        FROM
            "user"
        JOIN
            (
                chat_session
                JOIN
                    (
                        SELECT * FROM chat_message
                        WHERE chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                    ) as cm
                    ON chat_session.id = cm.chat_session_id
                LEFT JOIN
                    persona ON chat_session.persona_id = persona.id
                LEFT JOIN
                    sub_tool ON chat_session.sub_tool_id = sub_tool.sub_tool_id
            )
            ON "user".id = chat_session.user_id
            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
        WHERE
            LOWER("user".username) LIKE '%{search_query.lower()}%'
        GROUP BY
            "user".id, "user".username
        ORDER BY
            {order_by.value}
        OFFSET
            {offset}
        LIMIT
            {limit}
        """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()

    # Define the SQL query
    count_query = text(
        f"""
        SELECT
            COUNT(DISTINCT "user".id) as total_count
        FROM
            "user"
        JOIN
            (
                chat_session
                JOIN
                    (
                        SELECT * FROM chat_message
                        WHERE
                            chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                    ) as cm
                ON cm.chat_session_id = chat_session.id
            )
            ON "user".id = chat_session.user_id
            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
            AND LOWER("user".username) LIKE '%{search_query.lower()}%'
        """
    )

    total_count = (await db_session.execute(count_query)).scalar()

    max_val_query = text(
        f"""
        SELECT MAX(total_chat_messages) AS max_value
        FROM
            (
                SELECT
                    "user".id AS user_id,
                    COALESCE(COUNT(cm.id), 0) AS total_chat_messages
                FROM
                    "user"
                JOIN
                    (
                        chat_session
                        JOIN
                            (
                                SELECT * FROM chat_message
                                WHERE
                                    chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                            ) as cm
                            ON chat_session.id = cm.chat_session_id
                    )
                    ON "user".id = chat_session.user_id
                    AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
                    AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
                GROUP BY
                    "user".id
            ) AS sub_query
        """
    )

    max_value = (await db_session.execute(max_val_query)).scalar()

    # Perform transformation if a transformer function is provided
    items = [
        UserStat(
            user_id=row.user_id,
            username=row.username,
            total_chat_messages=row.total_chat_messages,
            total_token_usage=row.total_token_usage,
            total_number_of_personas=row.total_personas,
            total_number_of_sub_tools=row.total_sub_tools,
            total_number_of_tools=row.total_tools,
            total_chat_sessions=row.total_chat_sessions,
        )
        for row in rows
    ]
    meta_data: dict[str, int] = {
        "offset": offset,
        "limit": limit,
        "total": total_count,
        "returned": len(items),
        "max_value": max(max_value, 100),
    }

    # Create a Paginate object with metadata and paginated data
    response = Paginate[UserStat](meta_data=Meta(**meta_data), data=items)

    return response


async def get_user_stat_service(
    user_stat_request: UserStatRequest, db_session: AsyncSession
):
    res = []

    for user_id in user_stat_request.user_ids:
        user = await User.find(user_id=user_id, db_session=db_session)
        if not user:
            continue

        # Define the SQL query
        sql_query = text(
            f"""
            SELECT
                d.date,
                SUM(COALESCE(ms.token_usage, 0)) AS total_token_usage,
                COUNT(ms.*) as total_chat_messages,
                COUNT(DISTINCT ms.chat_session_id) AS total_chat_sessions,
                COUNT(DISTINCT ms.persona_id) AS total_personas,
                COUNT(DISTINCT ms.sub_tool_id) AS total_sub_tools,
                COUNT(DISTINCT ms.tool_id) AS total_tools
            FROM
                (SELECT generate_series(
                        '{user_stat_request.start_date}',
                        '{user_stat_request.end_date}',
                        '1 day'::interval
                    )::DATE AS date
                ) AS d
            LEFT JOIN
                (SELECT
                    timestamp,
                    token_usage,
                    chat_session_id,
                    persona_id,
                    chat_session.sub_tool_id AS sub_tool_id,
                    date_trunc('day', "user".created_at) AS sign_up_date,
                    tool_id
                FROM
                    chat_message
                    JOIN chat_session ON chat_session.id = chat_message.chat_session_id
                    LEFT JOIN persona ON persona.id = chat_session.persona_id
                    LEFT JOIN sub_tool ON sub_tool.sub_tool_id = chat_session.sub_tool_id
                    JOIN "user" ON "user".id = chat_session.user_id
                WHERE chat_session.user_id = '{str(user_id)}'
                ) AS ms
            ON d.date = date_trunc('day', ms.timestamp)
            GROUP BY d.date, ms.sign_up_date
            ORDER BY d.date LIMIT 1000
            """
        )

        # Execute the SQL query
        result = await db_session.execute(sql_query)
        rows = result.fetchall()

        user_stat_out = UserDailyStat(
            user_id=user_id,
            username=user.username,
            usage=[
                DailyUsage(
                    date=row.date,
                    total_chat_messages=row.total_chat_messages,
                    total_token_usage=row.total_token_usage,
                    total_number_of_personas=row.total_personas,
                    total_number_of_sub_tools=row.total_sub_tools,
                    total_number_of_tools=row.total_tools,
                    total_chat_sessions=row.total_chat_sessions,
                    signed_up_today=str(row.date) == str(user.created_at.date()),
                    active=(str(row.date) == str(user.created_at.date()))
                    or row.total_chat_messages > 0,
                )
                for row in rows
            ],
        )

        res.append(user_stat_out)
    return res


async def get_individual_user_stat_service(
    user_stat_request: List[IndividualRequest], db_session: AsyncSession
):
    res = []

    for request in user_stat_request:
        user = await User.find(user_id=request.user_id, db_session=db_session)
        if not user:
            continue

        # Define the SQL query
        sql_query = text(
            f"""
            SELECT
                DATE_TRUNC('day', chat_message.timestamp) as date,
                SUM(token_usage) as total_token_usage,
                COUNT(DISTINCT chat_session_id) as total_chat_sessions,
                COUNT(DISTINCT persona_id) as total_personas,
                COUNT(DISTINCT chat_session.sub_tool_id) as total_sub_tools,
                COUNT(DISTINCT tool_id) as total_tools,
                COUNT(chat_message.id) as total_chat_messages
            FROM
                chat_message
                JOIN chat_session ON chat_session.id = chat_message.chat_session_id
                LEFT JOIN persona ON persona.id = chat_session.persona_id
                LEFT JOIN sub_tool ON sub_tool.sub_tool_id = chat_session.sub_tool_id
                JOIN "user" ON "user".id = chat_session.user_id
            WHERE chat_session.user_id = '{str(request.user_id)}'
            GROUP BY
                DATE_TRUNC('day', chat_message.timestamp)
            ORDER BY
                DATE_TRUNC('day', chat_message.timestamp)
            OFFSET
                {request.offset}
            LIMIT
                {request.limit}
            """
        )

        # Define the SQL query
        count_query = text(
            """
            SELECT COUNT(DISTINCT DATE_TRUNC('day', chat_message.timestamp)) as total_count
            FROM
                chat_message 
            """
        )

        # Execute the SQL query
        result = await db_session.execute(sql_query)
        rows = result.fetchall()

        result = await db_session.execute(count_query)
        total_count = result.scalar()

        usage: List[IndividualDailyUsage] = [
            IndividualDailyUsage(
                date=row.date,
                total_chat_messages=row.total_chat_messages,
                total_token_usage=row.total_token_usage,
                total_number_of_personas=row.total_personas,
                total_number_of_sub_tools=row.total_sub_tools,
                total_number_of_tools=row.total_tools,
                total_chat_sessions=row.total_chat_sessions,
            )
            for row in rows
        ]

        user_stat_out = IndividualUserDailyStat(
            user_id=request.user_id,
            username=user.username,
            signed_up_date=user.created_at.date(),
            usage=usage,
            total=total_count,
            offset=request.offset,
            limit=request.limit,
            returned=len(usage),
        )

        res.append(user_stat_out)
    return res


async def user_daily_stat_service(
    user_stat_request: UserStatRequest, db_session: AsyncSession
):
    price_per_token = 0.0001

    # Define the sql query for the user daily stat for one user
    def build_query(user_id: str = ""):
        # convert user_stat_request.user_ids to a sql list of uuids
        user_ids = ", ".join([f"'{str(id)}'" for id in user_stat_request.user_ids])
        user_filter = (
            f"AND chat_session.user_id = '{str(user_id)}'"
            if user_id
            else f"AND chat_session.user_id IN ({user_ids})"
        )

        return text(
            f"""
            SELECT
                d.date,
                json_build_object(
                    'total_chat_messages', COALESCE(SUM(CASE WHEN chat_message.message_from = 1 THEN 1 ELSE 0 END), 0),
                    'total_token_usage', COALESCE(SUM(CASE WHEN chat_message.message_from = 1 THEN chat_message.token_usage ELSE 0 END), 0),
                    'total_chat_sessions', COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 1 THEN chat_session.id END), 0),
                    'total_price', COALESCE(SUM(CASE WHEN chat_message.message_from = 1 THEN chat_message.token_usage ELSE 0 END) * {price_per_token}, 0)
                ) AS telegram_bot,
                json_build_object(
                    'total_chat_messages', COALESCE(SUM(CASE WHEN chat_message.message_from = 2 THEN 1 ELSE 0 END), 0),
                    'total_token_usage', COALESCE(SUM(CASE WHEN chat_message.message_from = 2 THEN chat_message.token_usage ELSE 0 END), 0),
                    'total_chat_sessions', COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 2 THEN chat_session.id END), 0),
                    'total_price', COALESCE(SUM(CASE WHEN chat_message.message_from = 2 THEN chat_message.token_usage ELSE 0 END) * {price_per_token}, 0)
                ) AS telegram_mini_app,
                json_build_object(
                    'total_chat_messages', COALESCE(SUM(CASE WHEN chat_message.message_from = 3 THEN 1 ELSE 0 END), 0),
                    'total_token_usage', COALESCE(SUM(CASE WHEN chat_message.message_from = 3 THEN chat_message.token_usage ELSE 0 END), 0),
                    'total_chat_sessions', COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 3 THEN chat_session.id END), 0),
                    'total_price', COALESCE(SUM(CASE WHEN chat_message.message_from = 3 THEN chat_message.token_usage ELSE 0 END) * {price_per_token}, 0)
                ) AS mobile_app,
                json_build_object(
                    'total_chat_messages', COALESCE(COUNT(chat_message.id), 0),
                    'total_token_usage', COALESCE(
                        SUM(chat_message.token_usage), 0),
                    'total_chat_sessions', COALESCE(COUNT(DISTINCT chat_session.id), 0),
                    'total_price', COALESCE(
                        SUM(chat_message.token_usage) * {price_per_token}, 0)
                ) AS total
            FROM
                (
                    SELECT generate_series(
                        '{user_stat_request.start_date}',
                        '{user_stat_request.end_date}',
                        '1 day'::interval
                    )::DATE AS date
                ) AS d
            LEFT JOIN
                (
                    chat_message
                    JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                    {user_filter}
                )
                ON d.date = date_trunc('day', chat_message.timestamp)
            GROUP BY
                d.date
            ORDER BY
                d.date

            """
        )

    res = []

    # Execute the sql query for each user_id
    for user_id in user_stat_request.user_ids:
        user = await User.find(user_id=user_id, db_session=db_session)
        if not user:
            continue

        sql_query = build_query(user_id)
        result = await db_session.execute(sql_query)

        rows = result.fetchall()

        # Perform transformation if a transformer function is provided
        user_stat_response = UserStatResponse(
            user_id=user_id,
            username=user.username,
            usage=[
                DailyStat(
                    date=row.date,
                    telegram_bot=row.telegram_bot,
                    telegram_mini_app=row.telegram_mini_app,
                    mobile_app=row.mobile_app,
                    total=row.total,
                )
                for row in rows
            ],
        )

        res.append(user_stat_response)

    total_query = build_query()
    result = await db_session.execute(total_query)
    rows = result.fetchall()

    total = [
        DailyStat(
            date=row.date,
            telegram_bot=row.telegram_bot,
            telegram_mini_app=row.telegram_mini_app,
            mobile_app=row.mobile_app,
            total=row.total,
        )
        for row in rows
    ]

    return UserStatTotalResponse(users=res, total=total)


async def get_persona_chat_sessions_service(
    user_stat_request: UserPersonaStatRequest, db_session: AsyncSession
):
    # Define the SQL query
    start_date = user_stat_request.date
    end_date = start_date + timedelta(days=1)

    stmt = (
        select(ChatSession)
        .join(ChatMessage, ChatMessage.chat_session_id == ChatSession.id)
        .filter(
            ChatSession.user_id == user_stat_request.user_id,
            ChatSession.persona_id == user_stat_request.persona_id,
            (start_date <= ChatMessage.timestamp) & (ChatMessage.timestamp < end_date),
        )
        .distinct()
    )
    # Execute the SQL query
    result = await db_session.execute(stmt)
    # Fetch the results
    return result.scalars().all()


async def get_sub_tool_chat_sessions_service(
    user_stat_request: UserSubToolStatRequest, db_session: AsyncSession
):
    # Define the SQL query
    start_date = user_stat_request.date
    end_date = start_date + timedelta(days=1)

    stmt = (
        select(ChatSession)
        .join(ChatMessage, ChatMessage.chat_session_id == ChatSession.id)
        .filter(
            ChatSession.user_id == user_stat_request.user_id,
            ChatSession.sub_tool_id == user_stat_request.sub_tool_id,
            (start_date <= ChatMessage.timestamp) & (ChatMessage.timestamp < end_date),
        )
        .distinct()
    )
    # Execute the SQL query
    result = await db_session.execute(stmt)
    # Fetch the results
    return result.scalars().all()


async def get_chat_messages_service(
    user_stat_request: UserChatSessionRequest, db_session: AsyncSession
):
    # Define the SQL query
    start_date = user_stat_request.date
    end_date = start_date + timedelta(days=1)

    stmt = select(ChatMessage).filter(
        ChatMessage.chat_session_id == user_stat_request.chat_session_id,
        (start_date <= ChatMessage.timestamp) & (ChatMessage.timestamp < end_date),
    )
    # Execute the SQL query
    result = await db_session.execute(stmt)
    # Fetch the results
    return result.scalars().all()


async def get_chat_summary_service(
    user_stat_request: UserChatSessionRequest, db_session: AsyncSession
):
    start_date = user_stat_request.date
    end_date = start_date + timedelta(days=1)

    get_summarized_query = (
        select(SummarizedChatSessionSnapShot)
        .filter(
            SummarizedChatSessionSnapShot.chat_session_id
            == user_stat_request.chat_session_id,
            SummarizedChatSessionSnapShot.timestamp < end_date,
        )
        .order_by(SummarizedChatSessionSnapShot.timestamp.desc())
        .limit(1)
    )

    result = await db_session.execute(get_summarized_query)
    summarized_instance: SummarizedChatSessionSnapShot | None = (
        result.scalars().one_or_none()
    )

    stmt = (
        select(ChatMessage).filter(
            ChatMessage.chat_session_id == user_stat_request.chat_session_id,
            ChatMessage.timestamp < end_date,
        )
    ).order_by(ChatMessage.timestamp.asc())

    if summarized_instance:
        stmt = stmt.where(ChatMessage.timestamp > summarized_instance.timestamp)

    result = await db_session.execute(stmt)
    instance: List[ChatMessage] = list(result.scalars().all())

    if len(instance) == 0:
        return ChatSummaryOut(
            number_of_messages=0, summary="No messages on the requested date"
        )

    system_prompt = """
    You are a proficient assistant that generates concise summaries of important conversations in chat histories.
    """
    messages: List[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    if summarized_instance:
        messages.append(
            {"role": "assistant", "content": summarized_instance.summarized_content}
        )

    for chat_message in instance:
        messages.append({"role": chat_message.role, "content": chat_message.message})

    messages.append(
        {
            "role": "user",
            "content": """
            Summarize the above conversation in a few sent,
            Don't Include this message and the next response,
            make sure the summary is very short and concise
            """,
        }
    )

    # fast_api_logger.debug(messages)
    answer, _, _, _ = await make_request(
        messages=messages, max_tokens=1800, model=LLMModels.MISTRAL
    )

    return ChatSummaryOut(number_of_messages=len(instance), summary=answer)


async def get_engaged_personas_service(
    user_stat_request: UserStatRequest, db_session: AsyncSession
):
    user_id_list_to_str = ", ".join(
        [f"'{str(user_id)}'" for user_id in user_stat_request.user_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            persona.id AS persona_id,
            persona.full_name,
            COALESCE(COUNT(cs.cm_id), 0) AS total_chat_messages,
            COALESCE(SUM(cs.token_usage), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT cs.chat_session_id), 0) AS total_chat_sessions
        FROM
            persona
        JOIN (
            SELECT
                chat_session.persona_id,
                chat_session.id AS chat_session_id,
                chat_message.id AS cm_id,
                chat_message.token_usage
            FROM chat_session
            JOIN chat_message ON chat_session.id = chat_message.chat_session_id
            JOIN "user" ON chat_session.user_id = "user".id
            WHERE "user".id IN ({user_id_list_to_str})
            AND chat_message.timestamp BETWEEN '{user_stat_request.start_date}' AND '{user_stat_request.end_date}'
        ) AS cs
        ON persona.id = cs.persona_id
        GROUP BY
            persona.id, persona.full_name;

        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        UserPersonaStat(
            persona_id=row.persona_id,
            full_name=row.full_name,
            total_chat_messages=row.total_chat_messages,
            total_token_usage=row.total_token_usage,
            total_chat_sessions=row.total_chat_sessions,
        )
        for row in rows
    ]


async def get_engaged_sub_tools_service(
    user_stat_request: UserStatRequest, db_session: AsyncSession
):
    user_id_list_to_str = ", ".join(
        [f"'{str(user_id)}'" for user_id in user_stat_request.user_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            sub_tool.sub_tool_id,
            sub_tool.sub_tool_name,
            COALESCE(COUNT(cs.cm_id), 0) AS total_chat_messages,
            COALESCE(SUM(cs.token_usage), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT cs.chat_session_id), 0) AS total_chat_sessions
        FROM
            sub_tool
        JOIN (
            SELECT
                chat_session.sub_tool_id,
                chat_session.id AS chat_session_id,
                chat_message.id AS cm_id,
                chat_message.token_usage
            FROM chat_session
            JOIN chat_message ON chat_session.id = chat_message.chat_session_id
            JOIN "user" ON chat_session.user_id = "user".id
            WHERE "user".id IN ({user_id_list_to_str})
            AND chat_message.timestamp BETWEEN '{user_stat_request.start_date}' AND '{user_stat_request.end_date}'
        ) AS cs
        ON sub_tool.sub_tool_id = cs.sub_tool_id
        GROUP BY
            sub_tool.sub_tool_id, sub_tool.sub_tool_name;

        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        UserSubToolStat(
            sub_tool_id=row.sub_tool_id,
            sub_tool_name=row.sub_tool_name,
            total_chat_messages=row.total_chat_messages,
            total_token_usage=row.total_token_usage,
            total_chat_sessions=row.total_chat_sessions,
        )
        for row in rows
    ]


async def get_engaged_tools_service(
    user_stat_request: UserStatRequest, db_session: AsyncSession
):
    user_id_list_to_str = ", ".join(
        [f"'{str(user_id)}'" for user_id in user_stat_request.user_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            tool.tool_id,
            tool.tool_name,
            COALESCE(COUNT(cs.cm_id), 0) AS total_chat_messages,
            COALESCE(SUM(cs.token_usage), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT cs.chat_session_id), 0) AS total_chat_sessions
        FROM
            tool
        JOIN (
            SELECT
                sub_tool.tool_id,
                chat_session.id AS chat_session_id,
                chat_message.id AS cm_id,
                chat_message.token_usage
            FROM chat_session
            JOIN chat_message ON chat_session.id = chat_message.chat_session_id
            JOIN "user" ON chat_session.user_id = "user".id
            JOIN sub_tool ON chat_session.sub_tool_id = sub_tool.sub_tool_id
            WHERE "user".id IN ({user_id_list_to_str})
            AND chat_message.timestamp BETWEEN '{user_stat_request.start_date}' AND '{user_stat_request.end_date}'
        ) AS cs
        ON tool.tool_id = cs.tool_id
        GROUP BY
            tool.tool_id, tool.tool_name;

        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        UserToolStat(
            tool_id=row.tool_id,
            tool_name=row.tool_name,
            total_chat_messages=row.total_chat_messages,
            total_token_usage=row.total_token_usage,
            total_chat_sessions=row.total_chat_sessions,
        )
        for row in rows
    ]


async def get_message_counts_service(
    user_stat_request: UserStatRequest, db_session: AsyncSession
):
    user_id_list_to_str = ", ".join(
        [f"'{str(user_id)}'" for user_id in user_stat_request.user_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COUNT(CASE WHEN chat_message.message_from = 1
                  AND "user".id IN ({user_id_list_to_str})
                  THEN 1 END) AS number_of_telegram_bot_messages,
            COUNT(CASE WHEN chat_message.message_from = 2
                  AND "user".id IN ({user_id_list_to_str})
                  THEN 1 END) AS number_of_telegram_min_app_messages,
            COUNT(CASE WHEN chat_message.message_from = 3
                  AND "user".id IN ({user_id_list_to_str})
                  THEN 1 END) AS number_of_mobile_app_messages
        FROM
            (SELECT generate_series(
                    '{user_stat_request.start_date}',
                    '{user_stat_request.end_date}',
                    '1 day'::interval
                )::date AS date
            ) AS d
        LEFT JOIN
            (
                chat_message
                JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                JOIN "user" ON chat_session.user_id = "user".id
            )
            ON date_trunc('day', chat_message.timestamp) = d.date
        GROUP BY
            d.date
        ORDER BY
            d.date
        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        ChatMessageCount(
            period={"day": row.date.strftime("%Y-%m-%d")},
            number_of_telegram_bot_messages=row.number_of_telegram_bot_messages,
            number_of_telegram_min_app_messages=row.number_of_telegram_min_app_messages,
            number_of_mobile_app_messages=row.number_of_mobile_app_messages,
            total_number_of_messages=row.number_of_telegram_bot_messages
            + row.number_of_telegram_min_app_messages
            + row.number_of_mobile_app_messages,
        )
        for row in rows
    ]


async def get_total_tokens_service(
    user_stat_request: UserStatRequest, db_session: AsyncSession
):
    user_id_list_to_str = ", ".join(
        [f"'{str(user_id)}'" for user_id in user_stat_request.user_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 1
            AND "user".id IN ({user_id_list_to_str})
            THEN chat_message.token_usage ELSE 0 END), 0) AS total_telegram_bot_tokens,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 2
            AND "user".id IN ({user_id_list_to_str})
            THEN chat_message.token_usage ELSE 0 END), 0) AS total_telegram_mini_app_tokens,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 3
            AND "user".id IN ({user_id_list_to_str})
            THEN chat_message.token_usage ELSE 0 END), 0) AS total_mobile_app_tokens
        FROM
            (SELECT generate_series(
                    '{user_stat_request.start_date}',
                    '{user_stat_request.end_date}',
                    '1 day'::interval
                )::date AS date
            ) AS d
        LEFT JOIN
            (
                chat_message
                JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                JOIN "user" ON chat_session.user_id = "user".id
            )
            ON date_trunc('day', chat_message.timestamp) = d.date
        GROUP BY
            d.date
        ORDER BY
            d.date
        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        TotalTokenCount(
            period={"day": row.date.strftime("%Y-%m-%d")},
            total_telegram_bot_tokens=row.total_telegram_bot_tokens,
            total_telegram_mini_app_tokens=row.total_telegram_mini_app_tokens,
            total_mobile_app_tokens=row.total_mobile_app_tokens,
            total_tokens=row.total_telegram_bot_tokens
            + row.total_telegram_mini_app_tokens
            + row.total_mobile_app_tokens,
        )
        for row in rows
    ]


async def get_chat_session_counts_service(
    user_stat_request: UserStatRequest, db_session: AsyncSession
):
    user_id_list_to_str = ", ".join(
        [f"'{str(user_id)}'" for user_id in user_stat_request.user_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 1
            AND "user".id IN ({user_id_list_to_str})
            THEN chat_message.chat_session_id END), 0) AS number_of_active_telegram_bot_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 2
            AND "user".id IN ({user_id_list_to_str})
            THEN chat_message.chat_session_id END), 0) AS number_of_active_telegram_min_app_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 3
            AND "user".id IN ({user_id_list_to_str})
            THEN chat_message.chat_session_id END), 0) AS number_of_active_mobile_app_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN "user".id IN ({user_id_list_to_str})
            THEN chat_message.chat_session_id END), 0) AS total_number_of_active_sessions
        FROM
            (SELECT generate_series(
                    '{user_stat_request.start_date}',
                    '{user_stat_request.end_date}',
                    '1 day'::interval
                )::date AS date
            ) AS d
        LEFT JOIN
            (
                chat_message
                JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                JOIN "user" ON chat_session.user_id = "user".id
            )
            ON date_trunc('day', chat_message.timestamp) = d.date
        GROUP BY
            d.date
        ORDER BY
            d.date
        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        ChatSessionCount(
            period={"day": row.date.strftime("%Y-%m-%d")},
            number_of_active_telegram_bot_sessions=row.number_of_active_telegram_bot_sessions,
            number_of_active_telegram_min_app_sessions=row.number_of_active_telegram_min_app_sessions,
            number_of_active_mobile_app_sessions=row.number_of_active_mobile_app_sessions,
            total_number_of_active_sessions=row.total_number_of_active_sessions,
        )
        for row in rows
    ]


async def export_to_excel_service(
    start_date: date,
    end_date: date,
    db_session: AsyncSession,
    platform: Platform = Platform.ALL,
    include_developers: bool = False,
    include_archived: bool = False,
):
    platform_filter = ""
    if platform == Platform.TELEGRAM_BOT:
        platform_filter = "AND chat_message.message_from = 1"
    elif platform == Platform.TELEGRAM_MINI_APP:
        platform_filter = "AND chat_message.message_from = 2"
    elif platform == Platform.MOBILE_APP:
        platform_filter = "AND chat_message.message_from = 3"

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    writer = pd.ExcelWriter(temp_file.name, engine="openpyxl")
    size = 15

    sql_query = text(
        f"""
    WITH date_series AS (
        SELECT generate_series(
                '{start_date}'::date,  -- Replace with your start_date
                '{end_date}'::date,  -- Replace with your end_date
                '1 day'::interval
            )::date AS date
    )
    SELECT
        "user".id AS user_id,
        "user".username AS username,
        COALESCE(COUNT(DISTINCT CASE WHEN chat_message.timestamp::date = date_series.date THEN chat_session.id END), 0) AS session_count,
        date_series.date
    FROM
        "user"
    CROSS JOIN
        date_series
    LEFT JOIN
        (
            chat_session
            JOIN chat_message ON chat_message.chat_session_id = chat_session.id {platform_filter}
        )
        ON "user".id = chat_session.user_id
    WHERE ("user".is_developer = {include_developers} OR "user".is_developer = False)
        AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
    GROUP BY
        "user".id, "user".username, date_series.date
    ORDER BY
        "user".id, date_series.date;
    """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()
    columns = result.keys()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Pivot the DataFrame
    pivot_df = df.pivot(
        index="username", columns="date", values="session_count"
    ).fillna(0)
    pivot_df.columns = pd.to_datetime(pivot_df.columns).strftime("%Y-%m-%d")

    # Write the first DataFrame to the Excel file on Sheet1
    pivot_df.to_excel(
        writer, sheet_name="number of chat sessions", header=True, index_label=None
    )
    for column in writer.sheets["number of chat sessions"].columns:
        writer.sheets["number of chat sessions"].column_dimensions[
            column[0].column_letter
        ].width = size
    # Close the writer to save the Excel file

    sql_query = text(
        f"""
    WITH date_series AS (
        SELECT generate_series(
                '{start_date}'::date,  -- Replace with your start_date
                '{end_date}'::date,  -- Replace with your end_date
                '1 day'::interval
            )::date AS date
    )
    SELECT
        "user".id AS user_id,
        "user".username AS username,
        COALESCE(COUNT(CASE WHEN chat_message.timestamp::date = date_series.date THEN chat_message.id END), 0) AS message_count,
        date_series.date
    FROM
        "user"
    CROSS JOIN
        date_series
    LEFT JOIN
        (
            chat_session
            JOIN chat_message ON chat_message.chat_session_id = chat_session.id {platform_filter}
        )
        ON "user".id = chat_session.user_id
    WHERE ("user".is_developer = {include_developers} OR "user".is_developer = False)
        AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
    GROUP BY
        "user".id, "user".username, date_series.date
    ORDER BY
        "user".id, date_series.date;
    """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()
    columns = result.keys()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Pivot the DataFrame
    pivot_df = df.pivot(
        index="username", columns="date", values="message_count"
    ).fillna(0)
    pivot_df.columns = pd.to_datetime(pivot_df.columns).strftime("%Y-%m-%d")

    # Write the first DataFrame to the Excel file on Sheet1
    pivot_df.to_excel(
        writer, sheet_name="number of messages", header=True, index_label=None
    )
    for column in writer.sheets["number of messages"].columns:
        writer.sheets["number of messages"].column_dimensions[
            column[0].column_letter
        ].width = size

    sql_query = text(
        f"""
    WITH date_series AS (
        SELECT generate_series(
                '{start_date}'::date,  -- Replace with your start_date
                '{end_date}'::date,  -- Replace with your end_date
                '1 day'::interval
            )::date AS date
    )
    SELECT
        "user".id AS id,
        "user".username AS username,
        COALESCE(SUM(CASE WHEN chat_message.timestamp::date = date_series.date THEN chat_message.token_usage ELSE 0 END), 0) AS token_usage,
        date_series.date
    FROM
        "user"
    CROSS JOIN
        date_series
    LEFT JOIN
        (
            chat_session
            JOIN chat_message ON chat_message.chat_session_id = chat_session.id {platform_filter}
        )
        ON "user".id = chat_session.user_id
    WHERE ("user".is_developer = {include_developers} OR "user".is_developer = False)
        AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
    GROUP BY
        "user".id, "user".username, date_series.date
    ORDER BY
        "user".id, date_series.date;
    """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()
    columns = result.keys()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Pivot the DataFrame
    pivot_df = df.pivot(index="username", columns="date", values="token_usage").fillna(
        0
    )
    pivot_df.columns = pd.to_datetime(pivot_df.columns).strftime("%Y-%m-%d")

    # Write the first DataFrame to the Excel file on Sheet1
    pivot_df.to_excel(writer, sheet_name="token usage", header=True, index_label=None)
    for column in writer.sheets["token usage"].columns:
        writer.sheets["token usage"].column_dimensions[
            column[0].column_letter
        ].width = size

    # Close the writer to save the Excel file
    writer.close()

    return temp_file.name
