from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from app.constants import LLMModels, IMAGEModels

from app.routers.api_v1.chat.models import MessageFrom


class ChatSessionType(Enum):
    persona = "Persona"
    tool = "Tool"


class ChatCreate(BaseModel):
    question: str = Field(..., max_length=500)
    image_url: str = ""
    persona_id: UUID | None = None
    sub_tool_id: UUID | None = None
    message_from: MessageFrom = MessageFrom.MOBILE_APP
    model: LLMModels = LLMModels.MISTRAL
    image_model: IMAGEModels = IMAGEModels.STABLEDIFFUSION

    @field_validator("question")
    def validate_question(cls, v):
        if len(v) > 500:
            raise ValueError("First message is too long")
        return v


class ChatMessageBase(BaseModel):
    id: UUID
    role: str = Field(..., max_length=55)
    timestamp: datetime
    message: str = Field(..., max_length=10000)


class ChatMessageOutSchema(ChatMessageBase):
    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    id: UUID
    first_message: str = Field(..., max_length=10000)
    created_at: datetime
    updated_at: datetime
    is_pinned: bool
    share_able_link: str | None
    total_tokens: int
    user_id: UUID
    persona_id: UUID | None = None
    sub_tool_id: UUID | None = None


class DataSchema(BaseModel):
    chat_session_type: ChatSessionType
    name: str
    description: str
    picture: str


class ChatSessionBaseOutSchema(ChatSessionBase):
    data: DataSchema

    class Config:
        from_attributes = True


class ChatSessionOut(BaseModel):
    id: UUID
    chat_messages: list[ChatMessageBase]

    class Config:
        from_attributes = True


class SummerizedChatSessionSnapShotSchema(BaseModel):
    id: UUID
    chat_session_id: UUID
    summerized_content: str = Field(..., max_length=10000)
