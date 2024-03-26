from enum import Enum

from pydantic import BaseModel


class Partition(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class OverviewInfo(BaseModel):
    total_tokens: dict[str, int]
    number_of_users: dict[str, int]
    total_messages: dict[str, int]
    total_metrics: dict[str, int]


class UserCount(BaseModel):
    period: object
    number_of_telegram_bot_users: int
    number_of_telegram_min_app_users: int
    number_of_mobile_app_users: int
    total_number_of_users: int


class ChatMessageCount(BaseModel):
    period: object
    number_of_telegram_bot_messages: int
    number_of_telegram_min_app_messages: int
    number_of_mobile_app_messages: int
    total_number_of_messages: int


class ChatSessionCount(BaseModel):
    period: object
    number_of_active_telegram_bot_sessions: int
    number_of_active_telegram_min_app_sessions: int
    number_of_active_mobile_app_sessions: int
    total_number_of_active_sessions: int


class TotalTokenCount(BaseModel):
    period: object
    total_telegram_bot_tokens: int
    total_telegram_mini_app_tokens: int
    total_mobile_app_tokens: int
    total_tokens: int
