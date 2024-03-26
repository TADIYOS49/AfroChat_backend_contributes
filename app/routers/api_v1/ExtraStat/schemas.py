from uuid import UUID
from datetime import date
from pydantic import BaseModel


class PersonaStat(BaseModel):
    persona_id: UUID
    full_name: str
    total_chat_messages: int
    total_chat_sessions: int
    total_token_usage: int
    engaged_users: int


class SubToolStat(BaseModel):
    sub_tool_id: UUID
    sub_tool_name: str
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int
    engaged_users: int


class ToolStat(BaseModel):
    tool_id: UUID
    tool_name: str
    total_chat_messages: int
    total_token_usage: int
    total_chat_sessions: int
    engaged_users: int


class AverageInfo(BaseModel):
    messages: object
    sessions: object


class DailySignedUpUsers(BaseModel):
    date: date
    signed_up_users: int
