from datetime import date
from app.routers.api_v1.ExtraStat.schemas import (
    AverageInfo,
    DailySignedUpUsers,
    PersonaStat,
    SubToolStat,
    ToolStat,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.utils.logger import FastApiLogger


async def get_personas_service(
    start_date: date, end_date: date, db_session: AsyncSession
):
    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            persona.id AS persona_id,
            persona.full_name,
            COALESCE(COUNT(CASE WHEN NOT "user".is_developer THEN chat_message.id END), 0) AS total_chat_messages,
            COALESCE(COUNT(DISTINCT CASE WHEN NOT "user".is_developer THEN chat_message.chat_session_id END), 0) AS total_chat_sessions,
            COALESCE(SUM(CASE WHEN NOT "user".is_developer THEN chat_message.token_usage ELSE 0 END), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT CASE WHEN NOT "user".is_developer THEN "user".id END), 0) AS engaged_users
        FROM
            persona
        LEFT JOIN
            (
                chat_session
                JOIN
                    chat_message ON chat_message.chat_session_id = chat_session.id
                    AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}'
                JOIN
                    "user" ON chat_session.user_id = "user".id 
            )
            ON persona.id = chat_session.persona_id
        GROUP BY
            persona.id, persona.full_name
        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        PersonaStat(
            persona_id=row.persona_id,
            full_name=row.full_name,
            total_chat_messages=row.total_chat_messages,
            total_chat_sessions=row.total_chat_sessions,
            total_token_usage=row.total_token_usage,
            engaged_users=row.engaged_users,
        )
        for row in rows
    ]


async def get_sub_tools_service(
    start_date: date, end_date: date, db_session: AsyncSession
):
    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            sub_tool.sub_tool_id AS sub_tool_id,
            sub_tool.sub_tool_name,
            COALESCE(COUNT(CASE WHEN NOT "user".is_developer THEN chat_message.id END), 0) AS total_chat_messages,
            COALESCE(COUNT(DISTINCT CASE WHEN NOT "user".is_developer THEN chat_message.chat_session_id END), 0) AS total_chat_sessions,
            COALESCE(SUM(CASE WHEN NOT "user".is_developer THEN chat_message.token_usage ELSE 0 END), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT CASE WHEN NOT "user".is_developer THEN "user".id END), 0) AS engaged_users
        FROM
            sub_tool
        LEFT JOIN
            (
                chat_session
                JOIN
                    chat_message ON chat_message.chat_session_id = chat_session.id
                    AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}'
                JOIN
                    "user" ON chat_session.user_id = "user".id 
            )
            ON sub_tool.sub_tool_id = chat_session.sub_tool_id
        GROUP BY
            sub_tool.sub_tool_id, sub_tool.sub_tool_name
        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        SubToolStat(
            sub_tool_id=row.sub_tool_id,
            sub_tool_name=row.sub_tool_name,
            total_chat_messages=row.total_chat_messages,
            total_chat_sessions=row.total_chat_sessions,
            total_token_usage=row.total_token_usage,
            engaged_users=row.engaged_users,
        )
        for row in rows
    ]


async def get_tools_service(start_date: date, end_date: date, db_session: AsyncSession):
    # Define the SQL query
    sql_query = text(
        f"""
        SELECT
            tool.tool_id AS tool_id,
            tool.tool_name,
            COALESCE(COUNT(CASE WHEN NOT "user".is_developer THEN chat_message.id END), 0) AS total_chat_messages,
            COALESCE(COUNT(DISTINCT CASE WHEN NOT "user".is_developer THEN chat_message.chat_session_id END), 0) AS total_chat_sessions,
            COALESCE(SUM(CASE WHEN NOT "user".is_developer THEN chat_message.token_usage ELSE 0 END), 0) AS total_token_usage,
            COALESCE(COUNT(DISTINCT CASE WHEN NOT "user".is_developer THEN "user".id END), 0) AS engaged_users
        FROM
            tool
        LEFT JOIN
            (
                chat_session
                JOIN
                    chat_message ON chat_message.chat_session_id = chat_session.id
                    AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}'
                JOIN
                    "user" ON chat_session.user_id = "user".id
                JOIN 
                    sub_tool ON sub_tool.sub_tool_id = chat_session.sub_tool_id 
            )
            ON sub_tool.tool_id = tool.tool_id
        GROUP BY
            tool.tool_id, tool.tool_name
        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    rows = result.fetchall()

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        ToolStat(
            tool_id=row.tool_id,
            tool_name=row.tool_name,
            total_chat_messages=row.total_chat_messages,
            total_token_usage=row.total_token_usage,
            total_chat_sessions=row.total_chat_sessions,
            engaged_users=row.engaged_users,
        )
        for row in rows
    ]


async def get_average_info_service(
    start_date: date, end_date: date, db_session: AsyncSession
):
    # Define the SQL query
    sql_query = text(
        f"""            
        SELECT
            MIN(d.number_of_chat_messages) / 2 AS minimum_chat_messages,
            MAX(d.number_of_chat_messages) / 2 AS maximum_chat_messages,
            AVG(d.number_of_chat_messages) / 2 AS average_chat_messages,
            MIN(d.number_of_chat_sessions) / 2 AS minimum_chat_sessions,
            MAX(d.number_of_chat_sessions) / 2 AS maximum_chat_sessions,
            AVG(d.number_of_chat_sessions) / 2 AS average_chat_sessions
        FROM
            (
                SELECT
                        "user".id AS user_id,
                        "user".username AS username,
                        COUNT(chat_message.id) AS number_of_chat_messages,
                        COUNT(DISTINCT chat_session.id) AS number_of_chat_sessions 
                    FROM
                        chat_session
                        JOIN
                            chat_message ON chat_message.chat_session_id = chat_session.id
                            AND chat_message.timestamp BETWEEN '{start_date}' AND '{end_date}'
                        JOIN
                            "user" ON chat_session.user_id = "user".id
              			WHERE
              			    NOT "user".is_developer
                    GROUP BY
                        "user".id, "user".username
            ) AS d LIMIT 100   
        """
    )

    # Execute the SQL query
    result = await db_session.execute(sql_query)

    # Fetch the results
    row = result.fetchall()[0]

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return AverageInfo(
        messages={
            "minimum_chat_messages": row.minimum_chat_messages,
            "maximum_chat_messages": row.maximum_chat_messages,
            "average_chat_messages": row.average_chat_messages,
        },
        sessions={
            "minimum_chat_sessions": row.minimum_chat_sessions,
            "maximum_chat_sessions": row.maximum_chat_sessions,
            "average_chat_sessions": row.average_chat_sessions,
        },
    )


async def get_daily_signed_up_users_service(
    start_date: date, end_date: date, db_session: AsyncSession
):
    # Define the SQL query
    sql_query = text(
        f"""
        SELECT 
            d.date AS date,
            COALESCE(COUNT(CASE WHEN NOT "user".is_developer THEN 1 END), 0) AS signed_up_users
        FROM
            (SELECT generate_series(
                    '{start_date}',
                    '{end_date}',
                    '1 day'::interval
                )::date AS date
            ) AS d
        LEFT JOIN
            "user"
            ON date_trunc('day', "user".created_at) = d.date
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
    FastApiLogger.debug(result.keys())

    # Now, 'rows' contains the result set with columns 'date' and 'number_of_chatmessages'

    return [
        DailySignedUpUsers(date=row.date, signed_up_users=row.signed_up_users)
        for row in rows
    ]
