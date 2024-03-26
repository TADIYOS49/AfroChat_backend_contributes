import asyncio
from datetime import datetime
from sqlite3 import IntegrityError
import uuid

from sqlalchemy import func, select, text
from sqlalchemy.orm import selectinload
import aiohttp
import json
from app.bot.api_requests import make_request
from app.constants import LLMModels
from app.routers.api_v1.Ask.exceptions import (
    SESSION_NOT_FOUND,
    USER_NOT_OWNER_OF_SESSION,
)
from app.routers.api_v1.Ask.models import AskMessage, AskSession, Recommendation, Source
from app.routers.api_v1.Ask.schemas import (
    AskFollowUpRequest,
    AskRequest,
    AskResponse,
    Session,
    SessionType,
    SourceResponse,
    create_ask_response,
    create_session_response,
)
from app.routers.api_v1.Auth.models import User
from app.routers.api_v1.Auth.exceptions import RECAPTCHA_FAILED
from app.routers.api_v1.Service.schemas import Meta, Paginate
from app.routers.api_v1.Service.utils import paginate_response
from app.routers.api_v1.chat.models import ChatSession
<<<<<<< HEAD
from duckduckgo_search import DDGS, AsyncDDGS
=======
from duckduckgo_search import AsyncDDGS
>>>>>>> a7d0555a (change logic)

from app.utils.logger import FastApiLogger
from .constants import summary_prompt, recommendations_prompt
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.api_v1.Auth.service import verify_recaptcha


async def aget_results(query: str, max_results: int = 5):
<<<<<<< HEAD
    results = await AsyncDDGS(proxies=None).text(query, max_results=max_results)
    return results
=======
    async with AsyncDDGS() as ddgs:
        results = [r async for r in ddgs.text(query, max_results=max_results)]
        return results
>>>>>>> a7d0555a (change logic)


def get_summary_messages(question, search_results):
    search_results = "Search results: \n" + json.dumps(search_results)
    question = "Question: " + question

    messages = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": question},
        {"role": "system", "content": search_results},
    ]

    return messages


def get_recommendations_messages(question, search_results):
    search_results = "Search results: \n" + json.dumps(search_results)
    question = "Question: " + question

    user_message = search_results + "\n" + question

    messages = [
        {"role": "system", "content": recommendations_prompt},
        {"role": "user", "content": user_message},
    ]

    return messages


async def ask_model(question, model):
    # first search the internet
    results = await aget_results(question)

    # construct the summary messages
    summary_messages = get_summary_messages(question, results)

    # construct the recommendation messages
    recommendation_messages = get_recommendations_messages(question, results)

    # then call the model
    summary_response, recommendations_response = await asyncio.gather(
        make_request(summary_messages, model),
        make_request(recommendation_messages, model),
    )

    # Extract the response content
    summary, summary_tokens, _, _ = summary_response
    recommendations, recommendations_tokens, _, _ = recommendations_response

    # filter the recommended questions
    recommendations = filter(lambda x: "?" in x, recommendations.split("\n"))

    # remove non-alphabetical characters from the begining of every recommended question
    # define a function to do that
    def remove_non_alphabetical(string):
        idx = 0
        while idx < len(string) and not string[idx].isalpha():
            idx += 1

        return string[idx:]

    # apply the function to every recommended question
    recommendations = map(lambda x: remove_non_alphabetical(x), recommendations)

    return {
        "summary": summary,
        "sources": results,
        "recommendations": recommendations,
    }, summary_tokens + recommendations_tokens


async def ask_service(ask_request: AskRequest, user: User, db_session: AsyncSession):
<<<<<<< HEAD
    # validate the token
    if await verify_recaptcha(ask_request.recaptcha_token) is False:
        raise RECAPTCHA_FAILED

=======
>>>>>>> a7d0555a (change logic)
    response, total_tokens = await ask_model(ask_request.question, ask_request.model)

    try:
        new_session = AskSession(
            id=uuid.uuid4(),
            first_message=ask_request.question,
            user_id=user.id,
            total_tokens=total_tokens,
        )

        db_session.add(new_session)

        new_message = AskMessage(
            id=uuid.uuid4(),
            question=ask_request.question,
            ask_session_id=new_session.id,
            summary=response["summary"],
            token_usage=total_tokens,
            message_from=ask_request.message_from.value,
            llm_model=ask_request.model.value,
        )

        db_session.add(new_message)

        for source in response["sources"]:
            new_source = Source(
                title=source["title"],
                short_description=source["body"],
                URL=source["href"],
                ask_message_id=new_message.id,
            )
            db_session.add(new_source)

        for recomendation in response["recommendations"]:
            new_recomendation = Recommendation(
                question=recomendation,
                ask_message_id=new_message.id,
            )
            db_session.add(new_recomendation)

        db_session.add(new_session)

        await db_session.commit()

        # fetch the message together with the sources and recommendations from the database
        ask_message = (
            await db_session.execute(
                select(AskMessage)
                .options(
                    selectinload(AskMessage.sources),
                    selectinload(AskMessage.recommendations),
                )
                .where(AskMessage.id == new_message.id)
            )
        ).scalar_one()

        return create_ask_response(ask_message)
    except IntegrityError:
        # If an error occurred, roll back the transaction
        await db_session.rollback()
        raise


async def ask_follow_up_service(
    ask_follow_up_request: AskFollowUpRequest, user: User, db_session: AsyncSession
):
    response, total_tokens = await ask_model(
        ask_follow_up_request.question, ask_follow_up_request.model
    )

    # fetch the ask session with given id
    ask_session = await db_session.get(AskSession, ask_follow_up_request.ask_session_id)

    if not ask_session:
        raise SESSION_NOT_FOUND

    if ask_session.user_id != user.id:
        raise USER_NOT_OWNER_OF_SESSION

    try:
        new_message = AskMessage(
            id=uuid.uuid4(),
            question=ask_follow_up_request.question,
            ask_session_id=ask_session.id,
            summary=response["summary"],
            token_usage=total_tokens,
            message_from=ask_follow_up_request.message_from.value,
            llm_model=ask_follow_up_request.model.value,
        )

        db_session.add(new_message)

        for source in response["sources"]:
            new_source = Source(
                title=source["title"],
                short_description=source["body"],
                URL=source["href"],
                ask_message_id=new_message.id,
            )
            db_session.add(new_source)

        for recomendation in response["recommendations"]:
            new_recomendation = Recommendation(
                question=recomendation,
                ask_message_id=new_message.id,
            )
            db_session.add(new_recomendation)

        ask_session.updated_at = datetime.utcnow()
        await db_session.commit()

        # fetch the message together with the sources and recommendations from the database
        ask_message = (
            await db_session.execute(
                select(AskMessage)
                .options(
                    selectinload(AskMessage.sources),
                    selectinload(AskMessage.recommendations),
                )
                .where(AskMessage.id == new_message.id)
            )
        ).scalar_one()

        return create_ask_response(ask_message)

    except IntegrityError:
        # If an error occurred, roll back the transaction
        await db_session.rollback()
        raise


async def get_ask_messages_service(
    ask_session_id: uuid.UUID,
    user: User,
    db_session: AsyncSession,
    offset: int = 0,
    limit: int = 10,
):
    # get the ask_session
    ask_session = await db_session.get(AskSession, ask_session_id)

    if not ask_session:
        raise SESSION_NOT_FOUND

    # check if the user is the owner of the ask session
    if ask_session.user_id != user.id:
        raise USER_NOT_OWNER_OF_SESSION

    stmt = (
        select(AskMessage)
        .where(AskMessage.ask_session_id == ask_session_id)
        .options(
            selectinload(AskMessage.sources), selectinload(AskMessage.recommendations)
        )
        .order_by(AskMessage.created_at.desc())
    )

    def transformer(rows):
        return list(
            reversed([create_ask_response(ask_message) for ask_message in rows])
        )

    return await paginate_response(
        statement=stmt,
        db_session=db_session,
        model=AskResponse,
        offset=offset,
        limit=limit,
        transformer=transformer,
        to_orm=True,
    )


async def get_sessions_service(
    user: User, db_session: AsyncSession, offset: int = 0, limit: int = 10
):
    stmt = text(
        f"""
            select * from (
                SELECT c.id, c.first_message, c.created_at, c.updated_at, c.is_pinned, c.total_tokens, c.user_id, 
                c.persona_id, c.sub_tool_id, 'Chat' as type,
                (case when c.sub_tool_id ISNULL then 'Persona' else 'Tool' end) as chat_session_type,
                (case when c.sub_tool_id ISNULL then p.full_name else s.sub_tool_name end) as name,
                (case when c.sub_tool_id ISNULL then p.description else s.sub_tool_description end) as description,
                (case when c.sub_tool_id ISNULL then p.persona_image else s.sub_tool_image end) as image
                from chat_session c
                left join persona p on p.id = c.persona_id
                left join sub_tool s on s.sub_tool_id = c.sub_tool_id
                where c.user_id = '{user.id}'
                union
                SELECT a.id, 
                (
                    SELECT am.summary
                    FROM ask_message am
                    WHERE am.ask_session_id = a.id
                    ORDER BY am.created_at ASC
                    LIMIT 1
                ) as first_message,
                a.created_at, a.updated_at, a.is_pinned, a.total_tokens, a.user_id, 
                null, null, 'Ask' as type,
                null, a.first_message,
                a.first_message,
                'https://res.cloudinary.com/afrochat/image/upload/v1701867563/wwld5uwkhakuf4lufrxx.png'
                from ask_session a
                where a.user_id = '{user.id}'
            ) as query
            order by query.updated_at DESC
            offset {offset}
            limit {limit}
        """
    )

    # count all chat_sessions that belong to the user
    total_count = (
        await db_session.execute(
            select(func.count(ChatSession.id)).where(ChatSession.user_id == user.id)
        )
    ).scalar()

    # count all the ask_sessions that belong to the user
    total_count += (
        await db_session.execute(
            select(func.count(AskSession.id)).where(AskSession.user_id == user.id)
        )
    ).scalar()

    # Fetch the items
    items = await db_session.execute(stmt)
    items = items.fetchall()

    # Perform transformation if a transformer function is provided
    items = [create_session_response(session) for session in items]

    meta_data: dict[str, int] = {
        "offset": offset,
        "limit": limit,
        "total": total_count,
        "returned": len(items),
    }

    # Create a Paginate object with metadata and paginated data
    response = Paginate[Session](meta_data=Meta(**meta_data), data=items)

    return response


async def toggle_pin_service(
    session_id: uuid.UUID,
    session_type: SessionType,
    user: User,
    db_session: AsyncSession,
):
    if session_type == SessionType.CHAT:
        session = await db_session.get(ChatSession, session_id)
    else:
        session = await db_session.get(AskSession, session_id)

    if not session:
        raise SESSION_NOT_FOUND

    if session.user_id != user.id:
        raise USER_NOT_OWNER_OF_SESSION

    session.is_pinned = not session.is_pinned
    await db_session.commit()

    return {"success": True, "is_pinned": session.is_pinned}


async def get_pinned_sessions_service(
    user: User, db_session: AsyncSession, offset: int = 0, limit: int = 10
):
    stmt = text(
        f"""
            select * from (
                SELECT c.id, c.first_message, c.created_at, c.updated_at, c.is_pinned, c.total_tokens, c.user_id, 
                c.persona_id, c.sub_tool_id, 'Chat' as type,
                (case when c.sub_tool_id ISNULL then 'Persona' else 'Tool' end) as chat_session_type,
                (case when c.sub_tool_id ISNULL then p.full_name else s.sub_tool_name end) as name,
                (case when c.sub_tool_id ISNULL then p.description else s.sub_tool_description end) as description,
                (case when c.sub_tool_id ISNULL then p.persona_image else s.sub_tool_image end) as image
                from chat_session c
                left join persona p on p.id = c.persona_id
                left join sub_tool s on s.sub_tool_id = c.sub_tool_id
                where c.user_id = '{user.id}' and c.is_pinned = true
                union
                SELECT a.id, a.first_message, a.created_at, a.updated_at, a.is_pinned, a.total_tokens, a.user_id, 
                null, null, 'Ask' as type,
                null, a.first_message,
                (
                    SELECT am.summary
                    FROM ask_message am
                    WHERE am.ask_session_id = a.id
                    ORDER BY am.created_at ASC
                    LIMIT 1
                ) as description,
                'https://res.cloudinary.com/afrochat/image/upload/v1701867563/wwld5uwkhakuf4lufrxx.png'
                from ask_session a
                where a.user_id = '{user.id}' and a.is_pinned = true
            ) as query
            order by query.updated_at DESC
            offset {offset}
            limit {limit}
        """
    )

    # count all chat_sessions that belong to the user
    total_count = (
        await db_session.execute(
            select(func.count(ChatSession.id))
            .where(ChatSession.user_id == user.id)
            .where(ChatSession.is_pinned == True)
        )
    ).scalar()

    # count all the ask_sessions that belong to the user
    total_count += (
        await db_session.execute(
            select(func.count(AskSession.id))
            .where(AskSession.user_id == user.id)
            .where(AskSession.is_pinned == True)
        )
    ).scalar()

    # Fetch the items
    items = await db_session.execute(stmt)
    items = items.fetchall()

    # Perform transformation if a transformer function is provided
    items = [create_session_response(session) for session in items]

    meta_data: dict[str, int] = {
        "offset": offset,
        "limit": limit,
        "total": total_count,
        "returned": len(items),
    }

    # Create a Paginate object with metadata and paginated data
    response = Paginate[Session](meta_data=Meta(**meta_data), data=items)

    return response


async def delete_session_service(
    session_id: uuid.UUID,
    session_type: SessionType,
    user: User,
    db_session: AsyncSession,
):
    if session_type == SessionType.CHAT:
        session = await db_session.get(ChatSession, session_id)
    else:
        session = await db_session.get(AskSession, session_id)

    if not session:
        raise SESSION_NOT_FOUND

    if session.user_id != user.id:
        raise USER_NOT_OWNER_OF_SESSION

    await db_session.delete(session)
    await db_session.commit()

    return
