from datetime import date
import tempfile
import pandas as pd
from sqlalchemy import select
from app.routers.api_v1.Overview.schemas import (
    ChatMessageCount,
    ChatSessionCount,
    TotalTokenCount,
    UserCount,
)
from app.routers.api_v1.PersonaStat.schemas import (
    DailyStat,
    OrderBy,
    PersonaStat,
    PersonaStatRequest,
    PersonaStatResponse,
    PersonaStatTotalResponse,
    PlatformStat,
)
from app.routers.api_v1.Service.schemas import Meta, Paginate
from app.routers.api_v1.UserStat.schemas import Platform
from app.routers.api_v1.Persona.models import Persona

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


async def get_personas_service(
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
            persona.id AS persona_id,
            persona.full_name,
            COALESCE(COUNT(cm.id), 0) AS total_chat_messages,
            COALESCE(COUNT(DISTINCT cm.chat_session_id), 0) AS total_chat_sessions,
            COALESCE(SUM(cm.token_usage), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT "user".id), 0) AS engaged_users,
            CASE
                WHEN COALESCE(COUNT(DISTINCT "user".id), 0) > 0 THEN
                    CAST(COALESCE(COUNT(cm.id), 0) AS DECIMAL) / COUNT(DISTINCT "user".id)
                ELSE
                    0 -- or NULL, depending on your preference
            END AS chat_message_to_user_ratio
        FROM
            persona
        JOIN
            (
                chat_session
                JOIN
                    (
                        SELECT * FROM chat_message
                        WHERE chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                    ) as cm
                    ON chat_session.id = cm.chat_session_id
                JOIN
                    "user" ON (chat_session.user_id = "user".id)
                    AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
                    AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
            )
            ON persona.id = chat_session.persona_id
        GROUP BY
            persona.id, persona.full_name
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

    # Perform transformation if a transformer function is provided
    items = [
        PersonaStat(
            persona_id=row.persona_id,
            full_name=row.full_name,
            total_chat_messages=row.total_chat_messages,
            total_chat_sessions=row.total_chat_sessions,
            total_token_usage=row.total_token_usage,
            engaged_users=row.engaged_users,
            chat_message_to_user_ratio=row.chat_message_to_user_ratio,
        )
        for row in rows
    ]

    count_query = text(
        f"""
        SELECT
            COUNT(DISTINCT persona.id) AS total_count
        FROM
            persona
        JOIN
            (
                chat_session
                JOIN
                    (
                        SELECT * FROM chat_message
                        WHERE chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                    ) as cm
                    ON chat_session.id = cm.chat_session_id
                JOIN
                    "user" ON (chat_session.user_id = "user".id) 
                    AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
                    AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
            )
            ON persona.id = chat_session.persona_id
        """
    )

    total_count = (await db_session.execute(count_query)).scalar()

    # Define the SQL query
    max_val_query = text(
        f"""
        SELECT MAX(engaged_users) AS max_value
        FROM
            (
                SELECT
                    persona.id AS persona_id,
                    COALESCE(COUNT(DISTINCT "user".id), 0) AS engaged_users
                FROM
                    persona
                JOIN
                    (
                        chat_session
                        JOIN
                            (
                                SELECT * FROM chat_message
                                WHERE chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                            ) as cm
                            ON chat_session.id = cm.chat_session_id
                        JOIN
                            "user" ON (chat_session.user_id = "user".id) 
                            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
                            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
                    )
                    ON persona.id = chat_session.persona_id
                GROUP BY
                    persona.id
            ) AS sub_query
        """
    )

    max_value = (await db_session.execute(max_val_query)).scalar()

    meta_data: dict[str, int] = {
        "offset": offset,
        "limit": limit,
        "total": total_count,
        "returned": len(items),
        "max_value": max_value + 10,
    }

    # Create a Paginate object with metadata and paginated data
    response = Paginate[PersonaStat](meta_data=Meta(**meta_data), data=items)

    return response


async def search_personas_service(
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
            persona.id AS persona_id,
            persona.full_name,
            COALESCE(COUNT(cm.id), 0) AS total_chat_messages,
            COALESCE(COUNT(DISTINCT cm.chat_session_id), 0) AS total_chat_sessions,
            COALESCE(SUM(cm.token_usage), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT "user".id), 0) AS engaged_users,
            CASE
                WHEN COALESCE(COUNT(DISTINCT "user".id), 0) > 0 THEN
                    CAST(COALESCE(COUNT(cm.id), 0) AS DECIMAL) / COUNT(DISTINCT "user".id)
                ELSE
                    0 -- or NULL, depending on your preference
            END AS chat_message_to_user_ratio
        FROM
            persona
        JOIN
            (
                chat_session
                JOIN
                    (
                        SELECT * FROM chat_message
                        WHERE chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                    ) as cm
                    ON chat_session.id = cm.chat_session_id
                JOIN
                    "user" ON (chat_session.user_id = "user".id) 
                    AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
                    AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
            )
            ON persona.id = chat_session.persona_id
        WHERE
            LOWER(persona.full_name) LIKE '%{search_query.lower()}%'
        GROUP BY
            persona.id, persona.full_name
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

    # Perform transformation if a transformer function is provided
    items = [
        PersonaStat(
            persona_id=row.persona_id,
            full_name=row.full_name,
            total_chat_messages=row.total_chat_messages,
            total_chat_sessions=row.total_chat_sessions,
            total_token_usage=row.total_token_usage,
            engaged_users=row.engaged_users,
            chat_message_to_user_ratio=row.chat_message_to_user_ratio,
        )
        for row in rows
    ]

    count_query = text(
        f"""
        SELECT
            COUNT(DISTINCT persona.id) AS total_count
        FROM
            persona
        JOIN
            (
                chat_session
                JOIN
                    (
                        SELECT * FROM chat_message
                        WHERE chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                    ) as cm
                    ON chat_session.id = cm.chat_session_id
                JOIN
                    "user" ON (chat_session.user_id = "user".id) 
                    AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
                    AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
            )
            ON persona.id = chat_session.persona_id
            AND LOWER(persona.full_name) LIKE '%{search_query.lower()}%'
        """
    )

    total_count = (await db_session.execute(count_query)).scalar()

    # Define the SQL query
    max_val_query = text(
        f"""
        SELECT MAX(engaged_users) AS max_value
        FROM
            (
                SELECT
                    persona.id AS persona_id,
                    COALESCE(COUNT(DISTINCT "user".id), 0) AS engaged_users
                FROM
                    persona
                JOIN
                    (
                        chat_session
                        JOIN
                            (
                                SELECT * FROM chat_message
                                WHERE chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' {platform_filter}
                            ) as cm
                            ON chat_session.id = cm.chat_session_id
                        JOIN
                            "user" ON (chat_session.user_id = "user".id) 
                            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
                            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
                    )
                    ON persona.id = chat_session.persona_id
                GROUP BY
                    persona.id
            ) AS sub_query
        """
    )

    max_value = (await db_session.execute(max_val_query)).scalar()

    meta_data: dict[str, int] = {
        "offset": offset,
        "limit": limit,
        "total": total_count,
        "returned": len(items),
        "max_value": max_value + 10,
    }

    # Create a Paginate object with metadata and paginated data
    response = Paginate[PersonaStat](meta_data=Meta(**meta_data), data=items)

    return response


async def persona_daily_stat_service(
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession,
    include_developers: bool = False,
    include_archived: bool = False,
):
    """Get the daily statistics for a persona"""

    def build_query(
        start_date: date,
        end_date: date,
        price_per_token: float,
        persona_id: str = "",
        persona_id_list_to_str: str = "",
    ):
        """function to build the sql query"""
        persona_filter = (
            f"AND persona.id = '{persona_id}'"
            if persona_id
            else f"AND persona.id IN ({persona_id_list_to_str})"
        )

        return text(
            f"""
            SELECT
                d.date AS date,
                json_build_object(
                    'total_chat_messages', COALESCE(
                        SUM(
                            CASE
                                WHEN chat_message.message_from = 1 THEN 1
                            END
                        ), 0
                    ), 'total_chat_sessions', COALESCE(
                        COUNT(
                            DISTINCT CASE
                                WHEN chat_message.message_from = 1 THEN chat_session.id
                            END
                        ), 0
                    ), 'total_token_usage', COALESCE(
                        SUM(chat_message.token_usage), 0
                    ), 'total_engaged_users', COALESCE(
                        COUNT(
                            DISTINCT CASE
                                WHEN chat_message.message_from = 1 THEN chat_session.user_id
                            END
                        ), 0
                    ), 'total_price', COALESCE(
                        SUM(chat_message.token_usage) * {price_per_token}, 0
                    )
                ) AS telegram_bot,
                json_build_object(
                    'total_chat_messages', COALESCE(
                        SUM(
                            CASE
                                WHEN chat_message.message_from = 2 THEN 1
                            END
                        ), 0
                    ), 'total_chat_sessions', COALESCE(
                        COUNT(
                            DISTINCT CASE
                                WHEN chat_message.message_from = 2 THEN chat_session.id
                            END
                        ), 0
                    ), 'total_token_usage', COALESCE(
                        SUM(chat_message.token_usage), 0
                    ), 'total_engaged_users', COALESCE(
                        COUNT(
                            DISTINCT CASE
                                WHEN chat_message.message_from = 2 THEN chat_session.user_id
                            END
                        ), 0
                    ), 'total_price', COALESCE(
                        SUM(chat_message.token_usage) * {price_per_token}, 0
                    )
                ) AS telegram_mini_app,
                json_build_object(
                    'total_chat_messages', COALESCE(
                        SUM(
                            CASE
                                WHEN chat_message.message_from = 3 THEN 1
                            END
                        ), 0
                    ), 'total_chat_sessions', COALESCE(
                        COUNT(
                            DISTINCT CASE
                                WHEN chat_message.message_from = 3 THEN chat_session.id
                            END
                        ), 0
                    ), 'total_token_usage', COALESCE(
                        SUM(chat_message.token_usage), 0
                    ), 'total_engaged_users', COALESCE(
                        COUNT(
                            DISTINCT CASE
                                WHEN chat_message.message_from = 3 THEN chat_session.user_id
                            END
                        ), 0
                    ), 'total_price', COALESCE(
                        SUM(chat_message.token_usage) * {price_per_token}, 0
                    )
                ) AS mobile_app,
                json_build_object(
                    'total_chat_messages', COALESCE(COUNT(chat_message.id), 0), 'total_chat_sessions', COALESCE(
                        COUNT(DISTINCT chat_session.id), 0
                    ), 'total_token_usage', COALESCE(
                        SUM(chat_message.token_usage), 0
                    ), 'total_engaged_users', COALESCE(
                        COUNT(DISTINCT chat_session.user_id), 0
                    ), 'total_price', COALESCE(
                        SUM(chat_message.token_usage) * {price_per_token}, 0
                    )
                ) AS total
            FROM (
                    SELECT generate_series(
                            '{start_date}'::date, '{end_date}'::date, '1 day'::interval
                        )::date AS date
                ) AS d
                LEFT JOIN (
                    chat_message
                    JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                    JOIN persona ON chat_session.persona_id = persona.id
                    JOIN "user" u ON (chat_session.user_id = u.id)
                    AND (
                        u.is_developer = {include_developers}
                        OR u.is_developer = False
                    )
                    AND (
                        u.is_archived = {include_archived}
                        OR u.is_archived = False
                    )
                    {persona_filter}
                ) ON date_trunc('day', chat_message.timestamp) = d.date
            GROUP BY
                d.date
            ORDER BY d.date
            """
        )

    persona_stats = []

    for persona_id in persona_stat_request.persona_ids:
        persona = (
            await db_session.execute(select(Persona).filter(Persona.id == persona_id))
        ).scalar()

        if not persona:
            continue

        sql_query = build_query(
            start_date=persona_stat_request.start_date,
            end_date=persona_stat_request.end_date,
            price_per_token=0.0001,
            persona_id=str(persona_id),
        )

        result = await db_session.execute(sql_query)
        rows = result.fetchall()

        # Perform transformation if a transformer function is provided
        persona_stat = [
            DailyStat(
                date=row.date,
                telegram_bot=PlatformStat(**row.telegram_bot),
                telegram_mini_app=PlatformStat(**row.telegram_mini_app),
                mobile_app=PlatformStat(**row.mobile_app),
                total=PlatformStat(**row.total),
            )
            for row in rows
        ]

        persona_stats.append(
            PersonaStatResponse(
                persona_id=persona_id,
                full_name=persona.full_name,
                daily_stats=persona_stat,
            )
        )

    persona_id_list_to_str = ", ".join(
        [f"'{str(persona_id)}'" for persona_id in persona_stat_request.persona_ids]
    )
    total_query = build_query(
        start_date=persona_stat_request.start_date,
        end_date=persona_stat_request.end_date,
        price_per_token=0.0001,
        persona_id_list_to_str=persona_id_list_to_str,
    )

    result = await db_session.execute(total_query)
    rows = result.fetchall()

    # Perform transformation if a transformer function is provided
    total_stat = [
        DailyStat(
            date=row.date,
            telegram_bot=PlatformStat(**row.telegram_bot),
            telegram_mini_app=PlatformStat(**row.telegram_mini_app),
            mobile_app=PlatformStat(**row.mobile_app),
            total=PlatformStat(**row.total),
        )
        for row in rows
    ]

    return PersonaStatTotalResponse(personas=persona_stats, total=total_stat)


async def get_persona_users_service(
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession,
    include_developers: bool = False,
    include_archived: bool = False,
):
    persona_id_list_to_str = ", ".join(
        [f"'{str(persona_id)}'" for persona_id in persona_stat_request.persona_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT 
            d.date AS date,
            COUNT(DISTINCT CASE WHEN chat_message.message_from = 1 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_session.user_id END) AS number_of_telegram_bot_users,
            COUNT(DISTINCT CASE WHEN chat_message.message_from = 2 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_session.user_id END) AS number_of_telegram_min_app_users,
            COUNT(DISTINCT CASE WHEN chat_message.message_from = 3 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_session.user_id END) AS number_of_mobile_app_users,
            COUNT(DISTINCT CASE WHEN persona.id IN ({persona_id_list_to_str})
            THEN chat_session.user_id END) AS total_number_of_users
        FROM
            (SELECT generate_series(
                    '{persona_stat_request.start_date}',
                    '{persona_stat_request.end_date}',
                    '1 day'::interval
                )::date AS date
            ) AS d
        LEFT JOIN
            (
                chat_message
                JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                JOIN persona ON chat_session.persona_id = persona.id
                JOIN "user" u ON (chat_session.user_id = u.id)
                -- [OPTIONAL] Exclude developers and archived users
                AND (u.is_developer = {include_developers} OR u.is_developer = False)
                AND (u.is_archived = {include_archived} OR u.is_archived = False) 
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
        UserCount(
            period={"day": row.date.strftime("%Y-%m-%d")},
            number_of_telegram_bot_users=row.number_of_telegram_bot_users,
            number_of_telegram_min_app_users=row.number_of_telegram_min_app_users,
            number_of_mobile_app_users=row.number_of_mobile_app_users,
            total_number_of_users=row.total_number_of_users,
        )
        for row in rows
    ]


async def get_message_counts_service(
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession,
    include_developers: bool = False,
    include_archived: bool = False,
):
    persona_id_list_to_str = ", ".join(
        [f"'{str(persona_id)}'" for persona_id in persona_stat_request.persona_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COUNT(CASE WHEN chat_message.message_from = 1
                  AND persona.id IN ({persona_id_list_to_str})  
                  THEN 1 END) AS number_of_telegram_bot_messages,
            COUNT(CASE WHEN chat_message.message_from = 2 
                  AND persona.id IN ({persona_id_list_to_str}) 
                  THEN 1 END) AS number_of_telegram_min_app_messages,
            COUNT(CASE WHEN chat_message.message_from = 3
                  AND persona.id IN ({persona_id_list_to_str}) 
                  THEN 1 END) AS number_of_mobile_app_messages
        FROM
            (SELECT generate_series(
                    '{persona_stat_request.start_date}',
                    '{persona_stat_request.end_date}',
                    '1 day'::interval
                )::date AS date
            ) AS d
        LEFT JOIN
            (
                chat_message
                JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                JOIN persona ON chat_session.persona_id = persona.id
                JOIN "user" u ON (chat_session.user_id = u.id)
                -- [OPTIONAL] Exclude developers and archived users
                AND (u.is_developer = {include_developers} OR u.is_developer = False)
                AND (u.is_archived = {include_archived} OR u.is_archived = False)
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
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession,
    include_developers: bool = False,
    include_archived: bool = False,
):
    persona_id_list_to_str = ", ".join(
        [f"'{str(persona_id)}'" for persona_id in persona_stat_request.persona_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 1 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_message.token_usage ELSE 0 END), 0) AS total_telegram_bot_tokens,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 2 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_message.token_usage ELSE 0 END), 0) AS total_telegram_mini_app_tokens,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 3 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_message.token_usage ELSE 0 END), 0) AS total_mobile_app_tokens
        FROM
            (SELECT generate_series(
                    '{persona_stat_request.start_date}',
                    '{persona_stat_request.end_date}',
                    '1 day'::interval
                )::date AS date
            ) AS d
        LEFT JOIN
            (
                chat_message
                JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                JOIN persona ON chat_session.persona_id = persona.id
                JOIN "user" u ON (chat_session.user_id = u.id)
                -- [OPTIONAL] Exclude developers and archived users
                AND (u.is_developer = {include_developers} OR u.is_developer = False)
                AND (u.is_archived = {include_archived} OR u.is_archived = False)
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
    persona_stat_request: PersonaStatRequest,
    db_session: AsyncSession,
    include_developers: bool = False,
    include_archived: bool = False,
):
    persona_id_list_to_str = ", ".join(
        [f"'{str(persona_id)}'" for persona_id in persona_stat_request.persona_ids]
    )

    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 1 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_message.chat_session_id END), 0) AS number_of_active_telegram_bot_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 2 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_message.chat_session_id END), 0) AS number_of_active_telegram_min_app_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 3 
            AND persona.id IN ({persona_id_list_to_str})
            THEN chat_message.chat_session_id END), 0) AS number_of_active_mobile_app_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN persona.id IN ({persona_id_list_to_str})
            THEN chat_message.chat_session_id END), 0) AS total_number_of_active_sessions
        FROM
            (SELECT generate_series(
                    '{persona_stat_request.start_date}',
                    '{persona_stat_request.end_date}',
                    '1 day'::interval
                )::date AS date
            ) AS d
        LEFT JOIN
            (
                chat_message
                JOIN chat_session ON chat_message.chat_session_id = chat_session.id
                JOIN persona ON chat_session.persona_id = persona.id
                JOIN "user" u ON (chat_session.user_id = u.id)
                -- [OPTIONAL] Exclude developers and archived users
                AND (u.is_developer = {include_developers} OR u.is_developer = False)
                AND (u.is_archived = {include_archived} OR u.is_archived = False)
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
    rows = result.fetchall()

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
        persona.id AS persona_id,
        persona.full_name AS persona_name,
        COALESCE(COUNT(DISTINCT CASE WHEN chat_message.timestamp::date = date_series.date THEN chat_session.id END), 0) AS session_count,
        date_series.date
    FROM
        persona
    CROSS JOIN
        date_series
    LEFT JOIN
        (
            chat_session 
            JOIN chat_message ON chat_message.chat_session_id = chat_session.id {platform_filter}
            JOIN "user" ON chat_session.user_id = "user".id 
            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
        )
        ON persona.id = chat_session.persona_id
    GROUP BY
        persona.id, persona.full_name, date_series.date
    ORDER BY
        persona.id, date_series.date;
    """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()
    columns = result.keys()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Pivot the DataFrame
    pivot_df = df.pivot(
        index="persona_name", columns="date", values="session_count"
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
        persona.id AS persona_id,
        persona.full_name AS persona_name,
        COALESCE(COUNT(CASE WHEN chat_message.timestamp::date = date_series.date THEN chat_message.id END), 0) AS message_count,
        date_series.date
    FROM
        persona
    CROSS JOIN
        date_series
    LEFT JOIN
        (
            chat_session 
            JOIN chat_message ON chat_message.chat_session_id = chat_session.id {platform_filter}
            JOIN "user" ON chat_session.user_id = "user".id 
            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
        )
        ON persona.id = chat_session.persona_id
    GROUP BY
        persona.id, persona.full_name, date_series.date
    ORDER BY
        persona.id, date_series.date;
    """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()
    columns = result.keys()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Pivot the DataFrame
    pivot_df = df.pivot(
        index="persona_name", columns="date", values="message_count"
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

    # Close the writer to save the Excel fil

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
        persona.id AS persona_id,
        persona.full_name AS persona_name,
        COALESCE(COUNT(DISTINCT CASE WHEN chat_message.timestamp::date = date_series.date THEN "user".id END), 0) AS number_of_users,
        date_series.date
    FROM
        persona
    CROSS JOIN
        date_series
    LEFT JOIN
        (
            chat_session 
            JOIN chat_message ON chat_message.chat_session_id = chat_session.id {platform_filter}
            JOIN "user" ON chat_session.user_id = "user".id 
            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
        )
        ON persona.id = chat_session.persona_id
    GROUP BY
        persona.id, persona.full_name, date_series.date
    ORDER BY
        persona.id, date_series.date;
    """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()
    columns = result.keys()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Pivot the DataFrame
    pivot_df = df.pivot(
        index="persona_name", columns="date", values="number_of_users"
    ).fillna(0)
    pivot_df.columns = pd.to_datetime(pivot_df.columns).strftime("%Y-%m-%d")

    # Write the first DataFrame to the Excel file on Sheet1
    pivot_df.to_excel(
        writer, sheet_name="number of users", header=True, index_label=None
    )
    for column in writer.sheets["number of users"].columns:
        writer.sheets["number of users"].column_dimensions[
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
        persona.id AS persona_id,
        persona.full_name AS persona_name,
        COALESCE(SUM(CASE WHEN chat_message.timestamp::date = date_series.date THEN chat_message.token_usage ELSE 0 END), 0) AS token_usage,
        date_series.date
    FROM
        persona
    CROSS JOIN
        date_series
    LEFT JOIN
        (
            chat_session 
            JOIN chat_message ON chat_message.chat_session_id = chat_session.id {platform_filter}
            JOIN "user" ON chat_session.user_id = "user".id 
            AND ("user".is_developer = {include_developers} OR "user".is_developer = False)
            AND ("user".is_archived = {include_archived} OR "user".is_archived = False)
        )
        ON persona.id = chat_session.persona_id
    GROUP BY
        persona.id, persona.full_name, date_series.date
    ORDER BY
        persona.id, date_series.date;
    """
    )

    result = await db_session.execute(sql_query)
    rows = result.fetchall()
    columns = result.keys()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # Pivot the DataFrame
    pivot_df = df.pivot(
        index="persona_name", columns="date", values="token_usage"
    ).fillna(0)
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
