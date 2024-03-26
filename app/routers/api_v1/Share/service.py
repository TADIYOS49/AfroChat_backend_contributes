import uuid
from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.api_v1.Persona.exceptions import PERSONA_NOT_FOUND
from app.routers.api_v1.Share.exceptions import (
    CHAT_SESSION_NOT_FOUND,
    MESSAGE_SHARING_FAILED,
)
from app.routers.api_v1.chat.models import (
    ChatSession,
    ChatMessage,
)
from sqlalchemy.orm import selectinload


async def deep_copy_chat_session_messages(
    db_session: AsyncSession, chat_session_id: UUID, recipient_id: UUID
):
    # Check the owner of the chat session
    owner = await check_chat_session_owner(
        db_session=db_session, chat_session_id=chat_session_id, user_id=recipient_id
    )
    if owner:
        return chat_session_id

    # Retrieve the chat messages for the given chat_session_id
    chat_messages = await get_chat_messages(
        chat_session_id=chat_session_id, db_session=db_session
    )

    # Retrieve the persona_id for the given chat_session_id
    persona_id = await get_persona_id(
        chat_session_id=chat_session_id, db_session=db_session
    )

    chat_session_id = await create_new_session_id(
        user_id=recipient_id,
        chat_messages=chat_messages,
        persona_id=persona_id,
        db_session=db_session,
    )

    if chat_session_id:
        return chat_session_id
    else:
        raise MESSAGE_SHARING_FAILED


async def check_chat_session_owner(
    db_session: AsyncSession, chat_session_id: uuid.UUID, user_id: UUID
):
    stmt = (
        select(ChatSession)
        .where(ChatSession.id == chat_session_id, ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.persona), selectinload(ChatSession.sub_tool))
    )
    result = await db_session.execute(stmt)
    instance: ChatSession | None = result.scalars().one_or_none()
    if instance:
        return True
    return False


async def create_new_session_id(
    user_id: UUID, chat_messages, persona_id: UUID, db_session: AsyncSession
):
    db_chat_session: ChatSession = ChatSession(
        id=uuid.uuid4(),
        first_message=chat_messages[0].message,
        created_at=chat_messages[0].timestamp,
        total_tokens=chat_messages[0].token_usage,
        user_id=user_id,
        persona_id=persona_id,
    )

    db_session.add(db_chat_session)
    for message in chat_messages:
        db_session_message: ChatMessage = ChatMessage(
            role=message.role,
            timestamp=message.timestamp,
            message=message.message,
            token_usage=message.token_usage,
            chat_session_id=db_chat_session.id,
        )

        db_session.add(db_session_message)

    await db_session.commit()
    return db_chat_session.id


async def get_chat_messages(chat_session_id: UUID, db_session: AsyncSession):
    stmt_chat_session = (
        select(ChatMessage)
        .where(ChatMessage.chat_session_id == chat_session_id)
        .order_by(ChatMessage.timestamp.asc())
    )

    result_chat_session = await db_session.execute(statement=stmt_chat_session)
    result_chat_messages = result_chat_session.scalars().all()

    if not result_chat_messages:
        raise CHAT_SESSION_NOT_FOUND

    return result_chat_messages


async def get_persona_id(chat_session_id=UUID, db_session=AsyncSession):
    stmt_chat_session = select(ChatSession.persona_id).where(
        ChatSession.id == chat_session_id
    )

    result_chat_session = await db_session.execute(stmt_chat_session)
    persona_id_instance = result_chat_session.scalar()

    if not persona_id_instance:
        raise PERSONA_NOT_FOUND

    return persona_id_instance
