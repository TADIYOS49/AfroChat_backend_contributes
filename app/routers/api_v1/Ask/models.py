from enum import Enum
import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from app.constants import LLMModels
from app.routers.api_v1.Auth.models import User

from sqlalchemy import String, func, ForeignKey, INTEGER
from sqlalchemy import select, or_, and_, delete
from sqlalchemy.dialects.postgresql import UUID as sqlalchemy_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.database import Base


class MessageFrom(Enum):
    TELEGRAM_BOT = 1
    TELEGRAM_MINI_APP = 2
    MOBILE_APP = 3
    WEB_APP = 4


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    ask_message_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("ask_message.id"),
    )

    ask_message: Mapped["AskMessage"] = relationship(
        "AskMessage", back_populates="sources"
    )

    title: Mapped[str] = mapped_column(String(10000), nullable=False)
    short_description: Mapped[str] = mapped_column(String(10000), nullable=False)
    URL: Mapped[str] = mapped_column(String(10000), nullable=False)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    ask_message_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("ask_message.id"),
    )

    ask_message: Mapped["AskMessage"] = relationship(
        "AskMessage", back_populates="recommendations"
    )

    question: Mapped[str] = mapped_column(String(10000), nullable=False)


class AskMessage(Base):
    __tablename__ = "ask_message"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    question: Mapped[str] = mapped_column(String(10000), nullable=False)

    summary: Mapped[str] = mapped_column(String(10000), nullable=False)

    sources: Mapped[list["Source"]] = relationship(
        "Source",
        back_populates="ask_message",
        cascade="all, delete",
        passive_deletes=True,
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="ask_message",
        cascade="all, delete",
        passive_deletes=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    ask_session_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("ask_session.id"),
    )

    ask_session: Mapped["AskSession"] = relationship(
        "AskSession", back_populates="ask_messages"
    )

    token_usage: Mapped[int] = mapped_column(INTEGER, nullable=False)

    llm_model: Mapped[str] = mapped_column(
        String(100), server_default=LLMModels.MISTRAL.value, nullable=False
    )

    message_from: Mapped[int] = mapped_column(
        INTEGER, nullable=False, server_default="1"
    )


class AskSession(Base):
    __tablename__ = "ask_session"

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

    total_tokens: Mapped[int] = mapped_column(
        INTEGER, nullable=False, server_default="0"
    )

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
    )

    user: Mapped["User"] = relationship()

    ask_messages: Mapped[list["AskMessage"]] = relationship(
        "AskMessage",
        back_populates="ask_session",
        cascade="all, delete",
        passive_deletes=True,
    )
