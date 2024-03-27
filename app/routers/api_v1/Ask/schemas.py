from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID
from pydantic import BaseModel
from app.constants import LLMModels

from app.routers.api_v1.Ask.models import AskMessage, AskSession, MessageFrom


class AskRequest(BaseModel):
    question: str
    model: LLMModels = LLMModels.MISTRAL
    message_from: MessageFrom = MessageFrom.MOBILE_APP
    recaptcha_token: str | None = None


class AskFollowUpRequest(BaseModel):
    question: str
    model: LLMModels = LLMModels.MISTRAL
    message_from: MessageFrom = MessageFrom.MOBILE_APP
    ask_session_id: UUID


class SourceResponse(BaseModel):
    title: str
    short_description: str
    URL: str


class AskResponse(BaseModel):
    id: UUID
    ask_session_id: UUID
    question: str
    summary: str
    sources: List[SourceResponse]
    recommendations: List[str]
    created_at: datetime
    updated_at: datetime
    llm_model: str


def create_ask_response(ask_message: AskMessage):
    sources = [
        SourceResponse(
            title=source.title,
            short_description=source.short_description,
            URL=source.URL,
        )
        for source in ask_message.sources
    ]

    recommendations = [
        recommendation.question for recommendation in ask_message.recommendations
    ]
    return AskResponse(
        id=ask_message.id,
        ask_session_id=ask_message.ask_session_id,
        question=ask_message.question,
        summary=ask_message.summary,
        sources=sources,
        recommendations=recommendations,
        created_at=ask_message.created_at,
        updated_at=ask_message.updated_at,
        llm_model=ask_message.llm_model,
    )


class SessionType(Enum):
    CHAT = "Chat"
    ASK = "Ask"


class Session(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    first_message: str
    is_pinned: bool
    total_tokens: int
    type: str
    chat_session_type: str | None = None
    name: str
    description: str | None = None
    image: str
    persona_id: UUID | None = None
    sub_tool_id: UUID | None = None


def create_session_response(session):
    return Session(
        id=session.id,
        user_id=session.user_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        first_message=session.first_message,
        is_pinned=session.is_pinned,
        total_tokens=session.total_tokens,
        type=session.type,
        persona_id=session.persona_id,
        sub_tool_id=session.sub_tool_id,
        chat_session_type=session.chat_session_type,
        name=session.name,
        description=session.description,
        image=session.image,
    )
