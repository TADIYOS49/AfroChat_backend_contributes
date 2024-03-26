from enum import Enum
from typing import List
from datetime import date
from uuid import UUID

from pydantic import BaseModel, model_validator


class PlatformStat(BaseModel):
    total_chat_messages: int
    total_chat_sessions: int
    total_token_usage: int
    total_engaged_users: int
    total_price: float


class DailyStat(BaseModel):
    date: date
    telegram_bot: PlatformStat
    telegram_mini_app: PlatformStat
    mobile_app: PlatformStat
    total: PlatformStat


class ToolStatResponse(BaseModel):
    tool_id: UUID
    tool_name: str
    daily_stats: List[DailyStat]


class ToolStatTotalResponse(BaseModel):
    tool_stats: List[ToolStatResponse]
    total_stat: List[DailyStat]


class ToolStat(BaseModel):
    tool_id: UUID
    tool_name: str
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int
    engaged_users: int
    chat_message_to_user_ratio: float


class ToolStatRequest(BaseModel):
    start_date: date
    end_date: date
    tool_ids: List[UUID]

    # validation for start_date < end_date
    @model_validator(mode="before")
    def validate_dates(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")

        if start_date > end_date:
            raise ValueError("start_date must be less than end_date")

        return values


class OrderBy(str, Enum):
    TOOL_NAME_ASC = "tool_name asc"
    TOOL_NAME_DESC = "tool_name desc"
    POPULARITY_ASC = "engaged_users asc"
    POPULARITY_DESC = "engaged_users desc"
    TOTAL_TOKENS_ASC = "total_token_usage asc"
    TOTAL_TOKENS_DESC = "total_token_usage desc"
