from datetime import date
from app.routers.api_v1.Overview.schemas import (
    ChatMessageCount,
    ChatSessionCount,
    TotalTokenCount,
    UserCount,
    OverviewInfo,
)


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


async def get_overview_info_service(
    start_date: date, end_date: date, db_session: AsyncSession
):
    sql_query = text(
        f"""
        SELECT
            SUM(CASE WHEN 
            chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}'
            THEN chat_message.token_usage ELSE 0 END) AS total_tokens,
            
            SUM(CASE WHEN 
            chat_message.message_from = 1 
            AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' 
            THEN chat_message.token_usage ELSE 0 END) AS total_telegram_bot_tokens,
            
            SUM(CASE WHEN 
            chat_message.message_from = 2
            AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}'  
            THEN chat_message.token_usage ELSE 0 END) AS total_telegram_mini_app_tokens,
            
            SUM(CASE WHEN 
            chat_message.message_from = 3 
            AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' 
            THEN chat_message.token_usage ELSE 0 END) AS total_mobile_app_tokens,
            
            COUNT(CASE WHEN 
            chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' 
            THEN 1 END) AS total_messages,
            
            COUNT(CASE WHEN
            chat_message.message_from = 1 
            AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' 
            THEN 1 END) AS total_telegram_bot_messages,
            
            COUNT(CASE WHEN 
            chat_message.message_from = 2 
            AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' 
            THEN 1 END) AS total_telegram_mini_app_messages,
            
            COUNT(CASE WHEN 
            chat_message.message_from = 3
            AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}' 
            THEN 1 END) AS total_mobile_app_messages
        FROM chat_message
        JOIN chat_session ON chat_message.chat_session_id = chat_session.id
        JOIN "user" on chat_session.user_id = "user".id
        """
    )
    # Execute the SQL query
    result = await db_session.execute(sql_query)
    # Fetch the results
    message_row = result.fetchall()[0]

    sql_query = text(
        f"""
        SELECT COUNT(CASE WHEN created_at < '{end_date}' THEN 1 END) FROM "user"
        """
    )
    # Execute the SQL query
    result = await db_session.execute(sql_query)
    # Fetch the results
    total_number_of_users = result.scalar()

    sql_query = text(
        f"""
        SELECT COUNT(CASE WHEN 
            "user".created_at < '{end_date}' 
            AND "user".is_developer = false
            THEN 1 END) 
        FROM "user_telegram"
        JOIN "user" ON "user".id = "user_telegram".user_id 
        """
    )
    # Execute the SQL query
    result = await db_session.execute(sql_query)
    total_number_of_telegram_users = result.scalar()

    sql_query = text(
        f"""
        SELECT COUNT(CASE WHEN 
            "user".created_at < '{end_date}'
            AND "user".is_developer = false
            THEN 1 END) 
        FROM "user_email"
        JOIN "user" ON "user".id = "user_email".user_id 
        """
    )
    # Execute the SQL query
    result = await db_session.execute(sql_query)
    # Fetch the results
    total_number_of_mobile_users = result.scalar()

    sql_query = text(
        f"""
        SELECT COUNT(CASE WHEN created_at < '{end_date}' THEN 1 END) FROM "persona"
        """
    )
    # Execute the SQL query
    result = await db_session.execute(sql_query)
    # Fetch the results
    total_number_of_personas = result.scalar()

    sql_query = text(
        f"""
        SELECT COUNT(*) FROM "tool"
        """
    )
    # Execute the SQL query
    result = await db_session.execute(sql_query)
    # Fetch the results
    total_number_of_tools = result.scalar()

    sql_query = text(
        f"""
        SELECT COUNT(*) FROM "sub_tool"
        """
    )
    # Execute the SQL query
    result = await db_session.execute(sql_query)
    # Fetch the results
    total_number_of_subtools = result.scalar()

    return OverviewInfo(
        total_tokens={
            "total_tokens": message_row.total_tokens,
            "total_telegram_bot_tokens": message_row.total_telegram_bot_tokens,
            "total_telegram_mini_app_tokens": message_row.total_telegram_mini_app_tokens,
            "total_mobile_app_tokens": message_row.total_mobile_app_tokens,
        },
        number_of_users={
            "total_number_of_telegram_users": total_number_of_telegram_users,
            "total_number_of_mobile_users": total_number_of_mobile_users,
            "total_number_of_users": total_number_of_users,
        },
        total_messages={
            "total_messages": message_row.total_messages,
            "total_telegram_bot_messages": message_row.total_telegram_bot_messages,
            "total_telegram_mini_app_messages": message_row.total_telegram_mini_app_messages,
            "total_mobile_app_messages": message_row.total_mobile_app_messages,
        },
        total_metrics={
            "total_number_of_personas": total_number_of_personas,
            "total_number_of_tools": total_number_of_tools,
            "total_number_of_subtools": total_number_of_subtools,
        },
    )


async def get_active_user_counts_service(
    start_date: date, end_date: date, db_session: AsyncSession
):
    # Define the SQL query
    sql_query = text(
        f"""
        SELECT 
            d.date AS date,
            COUNT(DISTINCT CASE WHEN chat_message.message_from = 1 AND NOT "user".is_developer THEN chat_session.user_id END) AS number_of_telegram_bot_users,
            COUNT(DISTINCT CASE WHEN chat_message.message_from = 2 AND NOT "user".is_developer  THEN chat_session.user_id END) AS number_of_telegram_min_app_users,
            COUNT(DISTINCT CASE WHEN chat_message.message_from = 3 AND NOT "user".is_developer  THEN chat_session.user_id END) AS number_of_mobile_app_users,
            COUNT(DISTINCT CASE WHEN NOT "user".is_developer THEN chat_session.user_id END) AS total_number_of_users
        FROM
            (SELECT generate_series(
                    '{start_date}',
                    '{end_date}',
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
            d.date DESC
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
    start_date: date, end_date: date, db_session: AsyncSession
):
    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COUNT(CASE WHEN chat_message.message_from = 1 AND NOT "user".is_developer THEN 1 END) AS number_of_telegram_bot_messages,
            COUNT(CASE WHEN chat_message.message_from = 2 AND NOT "user".is_developer THEN 1 END) AS number_of_telegram_min_app_messages,
            COUNT(CASE WHEN chat_message.message_from = 3 AND NOT "user".is_developer THEN 1 END) AS number_of_mobile_app_messages
        FROM
            (SELECT generate_series(
                    '{start_date}',
                    '{end_date}',
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
            d.date DESC
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
    start_date: date, end_date: date, db_session: AsyncSession
):
    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 1 AND NOT "user".is_developer THEN chat_message.token_usage ELSE 0 END), 0) AS total_telegram_bot_tokens,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 2 AND NOT "user".is_developer THEN chat_message.token_usage ELSE 0 END), 0) AS total_telegram_mini_app_tokens,
            COALESCE(SUM(CASE WHEN chat_message.message_from = 3 AND NOT "user".is_developer THEN chat_message.token_usage ELSE 0 END), 0) AS total_mobile_app_tokens
        FROM
            (SELECT generate_series(
                    '{start_date}',
                    '{end_date}',
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
            d.date DESC
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
    start_date: date, end_date: date, db_session: AsyncSession
):
    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            d.date AS date,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 1 AND NOT "user".is_developer THEN chat_message.chat_session_id END), 0) AS number_of_active_telegram_bot_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 2 AND NOT "user".is_developer THEN chat_message.chat_session_id END), 0) AS number_of_active_telegram_min_app_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN chat_message.message_from = 3 AND NOT "user".is_developer THEN chat_message.chat_session_id END), 0) AS number_of_active_mobile_app_sessions,
            COALESCE(COUNT(DISTINCT CASE WHEN NOT "user".is_developer THEN chat_message.chat_session_id END), 0) AS total_number_of_active_sessions
        FROM
            (SELECT generate_series(
                    '{start_date}',
                    '{end_date}',
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
            d.date DESC
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
