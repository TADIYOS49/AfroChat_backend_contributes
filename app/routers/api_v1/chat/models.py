from enum import Enum
import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from app.constants import LLMModels
from app.routers.api_v1.Auth.models import User, UserTelegram

from sqlalchemy import BIGINT, String, func, ForeignKey, INTEGER
from sqlalchemy import select, or_, and_, delete
from sqlalchemy.dialects.postgresql import UUID as sqlalchemy_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.database import Base
from app.routers.api_v1.Persona.models import Persona
from app.routers.api_v1.Service.utils import paginate_response
from app.routers.api_v1.Tools.models import SubTool


class MessageFrom(Enum):
    TELEGRAM_BOT = 1
    TELEGRAM_MINI_APP = 2
    MOBILE_APP = 3
    WEB_APP = 4


class ChatSession(Base):
    __tablename__ = "chat_session"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    first_message: Mapped[str] = mapped_column(String(10000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    is_pinned: Mapped[bool] = mapped_column(server_default="false", nullable=False)
    share_able_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    total_tokens: Mapped[int] = mapped_column(
        INTEGER, nullable=False, server_default="0"
    )

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
    )
    user: Mapped["User"] = relationship()

    persona_id: Mapped[Optional[UUID]] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("persona.id")
    )
    persona: Mapped["Persona"] = relationship()

    sub_tool_id: Mapped[Optional[UUID]] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("sub_tool.sub_tool_id"),
        nullable=True,
    )
    sub_tool: Mapped[Optional["SubTool"]] = relationship()

    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="chat_session",
        cascade="all, delete",
        passive_deletes=True,
    )

    @classmethod
    async def find_by_user_id(cls, db_session: AsyncSession, user_id: UUID):
        stmt = (
            select(cls)
            .where(cls.user_id == user_id)
            .options(selectinload(cls.persona), selectinload(cls.sub_tool))
            .order_by(cls.created_at.desc())
        )
        result = await db_session.execute(stmt)
        instance: list[ChatSession] = list(result.scalars().all())
        return instance

    @classmethod
    async def find_by_id(
        cls,
        db_session: AsyncSession,
        chat_session_id: UUID,
        user_id: UUID,
    ):
        stmt = (
            select(cls)
            .where((cls.id == chat_session_id) & (cls.user_id == user_id))
            .options(selectinload(cls.persona), selectinload(cls.sub_tool))
        )
        result = await db_session.execute(stmt)
        instance: ChatSession | None = result.scalars().one_or_none()
        return instance

    @classmethod
    async def search_by_chat_message_2(
        cls, db_session: AsyncSession, chat_message: str, user_id: UUID
    ):
        from app.routers.api_v1.chat.schemas import ChatSessionBaseOutSchema

        stmt = (
            select(cls)
            .join(ChatMessage, ChatMessage.chat_session_id == cls.id)
            .options(selectinload(cls.persona), selectinload(cls.sub_tool))
            .where(
                and_(
                    cls.user_id == user_id,
                    or_(
                        and_(
                            cls.persona_id.isnot(None),
                            cls.persona.has(
                                and_(Persona.full_name.ilike(f"%{chat_message}%"))
                            ),
                        ),
                        and_(
                            cls.sub_tool_id.isnot(None),
                            cls.sub_tool.has(
                                and_(SubTool.sub_tool_name.ilike(f"%{chat_message}%"))
                            ),
                        ),
                        ChatMessage.message.ilike(f"%{chat_message}%"),
                    ),
                )
            )
            .distinct()
            .order_by(cls.created_at.desc())
        )
        return await paginate_response(
            statement=stmt,
            db_session=db_session,
            model=ChatSessionBaseOutSchema,
            offset=0,
            limit=10,
            transformer=lambda rows: [
                ChatSessionBaseOutSchema.model_validate(
                    ChatSessionOutModel(chat_session=chat_session),
                    from_attributes=True,
                )
                for chat_session in rows
            ],
            to_orm=True,
        )

    @classmethod
    async def get_pinned_chat_session(cls, db_session: AsyncSession, user_id: UUID):
        stmt = (
            select(cls)
            .where((cls.user_id == user_id) & cls.is_pinned)
            .options(selectinload(cls.persona), selectinload(cls.sub_tool))
            .order_by(cls.created_at.desc())
        )
        result = await db_session.execute(stmt)
        instance: list[ChatSession] = list(result.scalars().all())
        return instance

    @classmethod
    async def delete_chat_session_by_id(
        cls, db_session: AsyncSession, user_id: UUID, chat_session_id: UUID
    ) -> None:
        stmt = delete(cls).where(cls.user_id == user_id, cls.id == chat_session_id)

        await db_session.execute(statement=stmt)
        await db_session.commit()

    @classmethod
    async def get_user_last_session_with_persona(
        cls, db_session: AsyncSession, user_id: UUID, persona_id: UUID
    ):
        from app.routers.api_v1.chat.schemas import ChatSessionBaseOutSchema

        stmt = (
            select(cls)
            .where((cls.user_id == user_id) & (cls.persona_id == persona_id))
            .options(
                selectinload(ChatSession.persona), selectinload(ChatSession.sub_tool)
            )
            .order_by(cls.updated_at.desc())
            .limit(1)
        )
        result = await db_session.execute(stmt)
        instance: ChatSession | None = result.scalars().one_or_none()

        if instance is None:
            return None

        # transform to ChatSessionBaseOutSchema
        response = ChatSessionBaseOutSchema.model_validate(
            ChatSessionOutModel(chat_session=instance),
            from_attributes=True,
        )

        return response


class Data:
    def __init__(self, data: Persona | SubTool | None):
        from app.routers.api_v1.chat.schemas import ChatSessionType

        assert isinstance(data, Persona) or isinstance(data, SubTool)
        if isinstance(data, Persona):
            self.chat_session_type: ChatSessionType = ChatSessionType.persona
            self.name: str = data.full_name
            self.description: str = data.description
            self.picture: str = data.persona_image
        elif isinstance(data, SubTool):
            self.chat_session_type: ChatSessionType = ChatSessionType.tool
            self.name: str = data.sub_tool_name
            self.description: str = data.sub_tool_description
            self.picture: str = data.sub_tool_image


class ChatSessionOutModel:
    def __init__(self, chat_session: ChatSession):
        self.id: UUID = chat_session.id
        self.first_message: str = chat_session.first_message
        self.created_at: datetime = chat_session.created_at
        self.updated_at: datetime = chat_session.updated_at
        self.is_pinned: bool = chat_session.is_pinned
        self.share_able_link: str | None = chat_session.share_able_link
        self.total_tokens: int = chat_session.total_tokens
        self.user_id: UUID = chat_session.user_id
        self.persona_id: UUID | None = chat_session.persona_id
        self.sub_tool_id: UUID | None = chat_session.sub_tool_id
        self.user: User = chat_session.user
        # check if it is a persona or a sub_tool
        if chat_session.persona_id is not None:
            self.data = Data(chat_session.persona)
        elif chat_session.sub_tool_id is not None:
            self.data = Data(chat_session.sub_tool)


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    message: Mapped[str] = mapped_column(String(100000), nullable=False)
    token_usage: Mapped[int] = mapped_column(INTEGER, nullable=False)

    llm_model: Mapped[str] = mapped_column(
        String(100), server_default=LLMModels.MISTRAL.value, nullable=False
    )

    message_from: Mapped[int] = mapped_column(
        INTEGER, nullable=False, server_default="1"
    )
    chat_session_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("chat_session.id", ondelete="CASCADE")
    )
    chat_session: Mapped["ChatSession"] = relationship(
        "ChatSession", back_populates="chat_messages"
    )

    @classmethod
    async def get_all_messages_for_chat_session(
        cls, db_session: AsyncSession, chat_session_id: uuid.UUID
    ):
        stmt = (
            select(cls)
            .where(cls.chat_session_id == chat_session_id)
            .order_by(cls.timestamp.desc())
        )

        result = await db_session.execute(stmt)

        instance: list[ChatMessage] = list(result.scalars().all())
        # reverse the results
        instance = instance[::-1]
        return instance


class SummarizedChatSessionSnapShot(Base):
    __tablename__ = "summarized_chat_session_snap_shot"
    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    chat_session_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("chat_session.id", ondelete="CASCADE"),
    )
    summarized_content: Mapped[str] = mapped_column(String(10000), nullable=False)

    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    token_usage: Mapped[int] = mapped_column(INTEGER, nullable=False)


class TelegramGroupMessage(Base):
    __tablename__ = "telegram_group_message"
    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    telegram_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        index=True,
    )
    group_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        index=True,
    )
    group_name: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    group_topic: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        index=True,
        server_default="-1",
    )
    created_at: Mapped[int] = mapped_column(BIGINT, nullable=False)
    text: Mapped[str] = mapped_column(String(100000), nullable=False)
    telegram_user: Mapped["UserTelegram"] = relationship(
        "UserTelegram",
        back_populates="telegram_group_messages",
        primaryjoin="TelegramGroupMessage.telegram_id == foreign(cast(UserTelegram.telegram_id, BigInteger))",
    )

    @classmethod
    async def add_new_group_message(
        cls,
        db_session: AsyncSession,
        telegram_id: int,
        group_id: int,
        group_name: str,
        group_topic: int,
        created_at: int,
        text: str,
    ):
        db_telegram_message = TelegramGroupMessage(
            telegram_id=telegram_id,
            group_id=group_id,
            group_name=group_name,
            group_topic=group_topic,
            created_at=created_at,
            text=text,
        )
        try:
            db_session.add(db_telegram_message)
            await db_session.commit()
            return db_telegram_message
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise e

    # FIX ME: the limit might not be ideal
    @classmethod
    async def get_previous_conversations(
        cls,
        db_session: AsyncSession,
        group_id: int,
        group_topic: int,
        limit: int = 50,
    ):
        stmt = (
            select(cls)
            .options(selectinload(cls.telegram_user))
            .where(
                cls.group_id == group_id,
                cls.group_topic == group_topic,
            )
            .order_by(cls.created_at.desc())
            .limit(limit)
        )

        result = await db_session.execute(stmt)
        db_group_message: list[TelegramGroupMessage] = list(result.scalars().all())
        return db_group_message
