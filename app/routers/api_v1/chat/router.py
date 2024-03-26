from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Body, Query
from app.constants import LLMModels, IMAGEModels
from app.routers.api_v1.Auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.api_v1.Auth.dependencies import (
    get_activated_user,
    get_request_number_validated_user,
)
from app.routers.api_v1.Service.schemas import Paginate
from app.routers.api_v1.chat.constants import llm_models, image_models
from app.routers.api_v1.chat.exceptions import (
    CHAT_SESSION_NOT_FOUND,
    EMPTY_PERSONA_ID_AND_TOOL_ID,
    PERSONA_ID_AND_TOOL_ID_BOTH_FILLED,
)
from app.routers.api_v1.chat.models import ChatSession, MessageFrom
from app.routers.api_v1.chat.schemas import (
    ChatCreate,
    ChatSessionOut,
    ChatSessionBaseOutSchema,
    ChatMessageOutSchema,
)
from app.routers.api_v1.chat.service import (
    create_new_chat,
    ask_question_service,
    find_by_user_id,
    get_all_messages_for_chat_session,
    get_pinned_chat_session_service,
    get_session_id,
    check_chat_session_owner,
)

chat_router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)


# TODO refactor it based on the best practices
@chat_router.post(
    "/new_chat",
    response_model=ChatSessionOut,
    status_code=200,
)
async def create_chat(
    new_chat: ChatCreate,
    user: Annotated[User, Depends(get_request_number_validated_user)],
    db_session: AsyncSession = Depends(get_db),
):
    if new_chat.persona_id is None and new_chat.sub_tool_id is None:
        raise EMPTY_PERSONA_ID_AND_TOOL_ID
    if new_chat.persona_id is not None and new_chat.sub_tool_id is not None:
        raise PERSONA_ID_AND_TOOL_ID_BOTH_FILLED

    result = await create_new_chat(
        db_session=db_session,
        user_id=user.id,
        new_chat=new_chat,
    )

    return result


# get list of chat_sessions by user id
@chat_router.get(
    "/chat_history",
    response_model=Paginate[ChatSessionBaseOutSchema],
    response_model_exclude_none=True,
)
async def get_chat_sessions_by_user_id(
    user: Annotated[User, Depends(get_activated_user)],
    db_session: AsyncSession = Depends(get_db),
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await find_by_user_id(
        db_session=db_session, user_id=user.id, limit=limit, offset=offset
    )


@chat_router.get(
    "/chat_history/{chat_session_id}",
    response_model=Paginate[ChatMessageOutSchema],
)
async def get_chat_message(
    chat_session_id: UUID,
    user: Annotated[User, Depends(get_activated_user)],
    db_session: AsyncSession = Depends(get_db),
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    await check_chat_session_owner(
        db_session=db_session, chat_session_id=chat_session_id, user_id=user.id
    )

    return await get_all_messages_for_chat_session(
        db_session=db_session,
        chat_session_id=chat_session_id,
        limit=limit,
        offset=offset,
    )


@chat_router.post("/ask", response_model=list[ChatMessageOutSchema])
async def ask_question(
    worker: BackgroundTasks,
    chat_session_id: Annotated[UUID, Body()],
    question: Annotated[str, Body()],
    user: Annotated[User, Depends(get_request_number_validated_user)],
    db_session: AsyncSession = Depends(get_db),
    message_from: Annotated[MessageFrom, Body()] = MessageFrom.MOBILE_APP,
    model: Annotated[LLMModels, Body()] = LLMModels.MISTRAL,
    image_model: Annotated[IMAGEModels, Body()] = IMAGEModels.STABLEDIFFUSION,
):
    return await ask_question_service(
        db_session=db_session,
        chat_session_id=chat_session_id,
        question=question,
        user_id=user.id,
        worker=worker,
        message_from=message_from,
        current_model=model,
        image_model=image_model,
    )


@chat_router.put("/toggle_pin", response_model=dict[str, str])
async def toggle_pin(
    chat_session_id: Annotated[UUID, Body(embed=True)],
    user: Annotated[User, Depends(get_activated_user)],
    db_session: AsyncSession = Depends(get_db),
):
    db_chat_session: ChatSession | None = await ChatSession.find_by_id(
        db_session=db_session, chat_session_id=chat_session_id, user_id=user.id
    )
    if not db_chat_session:
        raise CHAT_SESSION_NOT_FOUND

    db_chat_session.is_pinned = not db_chat_session.is_pinned
    await db_session.commit()

    status = "pinned" if db_chat_session.is_pinned else "unpinned"

    return {"message": f"Chat session {status} successfully"}


@chat_router.get(
    "/get_pinned_chat_session",
    response_model=Paginate[ChatSessionBaseOutSchema],
    response_model_exclude_none=True,
)
async def get_pinned_chat_session(
    user: Annotated[User, Depends(get_activated_user)],
    db_session: AsyncSession = Depends(get_db),
):
    return await get_pinned_chat_session_service(db_session, user.id)


@chat_router.get(
    "/search",
    response_model=Paginate[ChatSessionBaseOutSchema],
)
async def search_chat(
    search_query: Annotated[str, Query()],
    user: Annotated[User, Depends(get_activated_user)],
    db_session: AsyncSession = Depends(get_db),
):
    search_result = await ChatSession.search_by_chat_message_2(
        db_session=db_session, chat_message=search_query, user_id=user.id
    )
    return search_result


@chat_router.post("/ask/afrochat", response_model=list[ChatMessageOutSchema])
async def chat_afrochat(
    question: Annotated[str, Body()],
    worker: BackgroundTasks,
    user: Annotated[User, Depends(get_request_number_validated_user)],
    db_session: AsyncSession = Depends(get_db),
):
    chat_session_id = await get_session_id(user, db_session, question)

    return await ask_question_service(
        db_session=db_session,
        chat_session_id=chat_session_id,
        question=question,
        user_id=user.id,
        worker=worker,
        message_from=MessageFrom.MOBILE_APP,
        current_model=LLMModels.MISTRAL,
    )


@chat_router.delete("/delete", response_model=str)
async def delete_chat(
    chat_session_id: Annotated[UUID, Query()],
    user: Annotated[User, Depends(get_activated_user)],
    db_session: AsyncSession = Depends(get_db),
):
    await ChatSession.delete_chat_session_by_id(
        db_session=db_session, user_id=user.id, chat_session_id=chat_session_id
    )

    return "Delete successful"


@chat_router.get("/models", dependencies=[Depends(get_activated_user)])
async def get_models(
    model_type: Annotated[str, Query()] = "llm_models",
):
    if model_type == "llm_models":
        return llm_models
    elif model_type == "image_models":
        return image_models
