from enum import Enum
from typing import List
from datetime import date
from uuid import UUID

from pydantic import BaseModel, model_validator


class UserStat(BaseModel):
    user_id: UUID
    username: str
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int
    total_number_of_personas: int
    total_number_of_sub_tools: int
    total_number_of_tools: int


class UserStatRequest(BaseModel):
    start_date: date
    end_date: date
    user_ids: List[UUID]

    @model_validator(mode="before")
    def validate_dates(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")

        if start_date > end_date:
            raise ValueError("start_date must be less than end_date")

        return values


class PlatformStat(BaseModel):
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int
    total_price: float


class DailyStat(BaseModel):
    date: date
    telegram_bot: PlatformStat
    telegram_mini_app: PlatformStat
    mobile_app: PlatformStat
    total: PlatformStat


class UserStatResponse(BaseModel):
    user_id: UUID
    username: str
    usage: List[DailyStat]


class UserStatTotalResponse(BaseModel):
    users: List[UserStatResponse]
    total: List[DailyStat]


class IndividualRequest(BaseModel):
    user_id: UUID
    offset: int
    limit: int


class IndividualStatRequest(BaseModel):
    data: List[IndividualRequest]


class UserPersonaStat(BaseModel):
    persona_id: UUID
    full_name: str
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int


class UserSubToolStat(BaseModel):
    sub_tool_id: UUID
    sub_tool_name: str
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int


class UserToolStat(BaseModel):
    tool_id: UUID
    tool_name: str
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int


class DailyUsage(BaseModel):
    date: date
    active: bool
    signed_up_today: bool
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int
    total_number_of_personas: int
    total_number_of_sub_tools: int
    total_number_of_tools: int


class IndividualDailyUsage(BaseModel):
    date: date
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int
    total_number_of_personas: int
    total_number_of_sub_tools: int
    total_number_of_tools: int


class UserDailyStat(BaseModel):
    user_id: UUID
    username: str
    usage: List[DailyUsage]


class IndividualUserDailyStat(BaseModel):
    user_id: UUID
    username: str
    signed_up_date: date
    usage: List[IndividualDailyUsage]
    total: int
    offset: int
    limit: int
    returned: int


class UserPersonaStatRequest(BaseModel):
    user_id: UUID
    persona_id: UUID
    date: date


class UserSubToolStatRequest(BaseModel):
    user_id: UUID
    sub_tool_id: UUID
    date: date


class UserChatSessionRequest(BaseModel):
    user_id: UUID
    chat_session_id: UUID
    date: date


class ChatSummaryOut(BaseModel):
    number_of_messages: int
    summary: str


class OrderBy(str, Enum):
    USERNAME_ASC = "username asc"
    USERNAME_DESC = "username desc"
    TOTAL_MESSAGES_ASC = "total_chat_messages asc"
    TOTAL_MESSAGES_DESC = "total_chat_messages desc"
    TOTAL_TOKENS_ASC = "total_token_usage asc"
    TOTAL_TOKENS_DESC = "total_token_usage desc"


class Platform(str, Enum):
    TELEGRAM_BOT = "telegram_bot"
    TELEGRAM_MINI_APP = "telegram_mini_app"
    MOBILE_APP = "mobile_app"
    ALL = "total"
