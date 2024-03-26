from enum import Enum
from typing import Annotated, List
from uuid import UUID
from fastapi import Body

from pydantic import BaseModel, Field


class ToolCreate(BaseModel):
    tool_name: str = Field(..., max_length=100)
    tool_desc: str = Field(..., max_length=5000)
    tool_image: str = Field(..., max_length=200)
    default_color: str = Field(..., max_length=10)
    is_premium: bool = False


class ToolEdit(ToolCreate):
    tool_id: UUID


class SubToolCreate(BaseModel):
    tool_id: UUID
    sub_tool_name: str = Field(..., max_length=100)
    sub_tool_description: str = Field(..., max_length=5000)
    sub_tool_initial_prompt: str = Field(..., max_length=10000)
    sub_tool_image: str = Field(..., max_length=200)
    is_premium: bool = False


class SubToolMulipleCreate(BaseModel):
    data: List[Annotated[SubToolCreate, Body()]]


class SubToolEdit(SubToolCreate):
    sub_tool_id: UUID


class SubToolOut(SubToolCreate):
    sub_tool_id: UUID

    class Config:
        from_attributes = True


class ToolOut(ToolCreate):
    tool_id: UUID
    sub_tools: List[SubToolOut]

    class Config:
        from_attributes = True


class ToolCreateOut(ToolCreate):
    tool_id: UUID


class SubToolOutAddInfo(SubToolOut):
    tool: ToolCreateOut

    class Config:
        from_attributes = True


class ToolOrderBy(str, Enum):
    TOOL_NAME_ASC = "tool_name_asc"
    TOOL_NAME_DESC = "tool_name_desc"


class SubToolOrderBy(str, Enum):
    SUB_TOOL_NAME_ASC = "sub_tool_name_asc"
    SUB_TOOL_NAME_DESC = "sub_tool_name_desc"
    TOOL_NAME_ASC = "tool_name_asc"
    TOOL_NAME_DESC = "tool_name_desc"
