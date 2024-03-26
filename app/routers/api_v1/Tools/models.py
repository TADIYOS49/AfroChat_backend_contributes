from collections import defaultdict
import uuid
from typing import List
from sqlalchemy import ForeignKey, Integer, false
from app.constants import LLMModels
from app.routers.api_v1.Tools.schemas import SubToolOutAddInfo, ToolCreateOut
from app.routers.api_v1.Service.utils import paginate_response
from sqlalchemy import ForeignKey
from sqlalchemy import true, Boolean
from sqlalchemy import String, select, or_, and_
from sqlalchemy.dialects.postgresql import UUID as sqlalchemy_UUID
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.database.base import Base
from sqlalchemy.sql import text


class Tool(Base):
    __tablename__ = "tool"

    tool_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    tool_name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    tool_desc: Mapped[str] = mapped_column(String(5000), nullable=False)
    tool_image: Mapped[str] = mapped_column(String(200), nullable=False)
    default_color: Mapped[str] = mapped_column(String(10), nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=true(), nullable=False
    )
    is_premium: Mapped[bool] = mapped_column(server_default=false(), nullable=False)

    # Relationship of tools with sub-tools
    sub_tools: Mapped[List["SubTool"]] = relationship(
        "SubTool", back_populates="tool", cascade="all,delete"
    )

    # Read method that aggregates tools and sub-tools from the db
    @classmethod
    async def get_all(cls, db_session: AsyncSession, isArchived: bool = False):
        if isArchived:
            statement = (
                select(cls).options(selectinload(cls.sub_tools)).filter(~cls.is_active)
            )
        else:
            statement = (
                select(cls).options(selectinload(cls.sub_tools)).filter(cls.is_active)
            )

        result = await db_session.execute(statement)
        instance: List[Tool] = list(result.scalars().all())

        if not isArchived:
            for tool in instance:
                tool.sub_tools = [
                    sub_tool for sub_tool in tool.sub_tools if not sub_tool.is_archived
                ]

            instance = [tool for tool in instance if len(tool.sub_tools) != 0]

        return instance

    @classmethod
    async def get_all_admin_paginated(
        cls,
        db_session: AsyncSession,
        tool_name: str,
        order_by_clause,
        offset: int = 0,
        is_archived: bool = False,
        limit: int = 10,
    ):
        from .schemas import ToolOut

        stmt = (
            select(cls)
            .options(selectinload(cls.sub_tools))
            .where(
                and_(
                    cls.is_active == (not is_archived),
                    cls.tool_name.ilike(f"%{tool_name}%"),
                )
            )
        )

        return await paginate_response(
            statement=stmt,
            db_session=db_session,
            model=ToolOut,
            offset=offset,
            limit=limit,
            sorting_attribute=order_by_clause,
            to_orm=True,
        )

    @classmethod
    async def get_all_admin(cls, db_session: AsyncSession, order_by_clause):
        statement = select(cls).options(selectinload(cls.sub_tools))
        result = await db_session.execute(statement)
        instance: List[Tool] = list(result.scalars().all())

        return instance

    # Find a tool by the tool name which is unique.
    @classmethod
    async def find_by_name(cls, db_session, tool_name):
        statement = select(cls).where((cls.tool_name == tool_name))

        result = await db_session.execute(statement)

        instance: Tool | None = result.scalars().first()

        return instance

    # Find a tool by the tool id.
    @classmethod
    async def find_by_id(cls, db_session, tool_id):
        statement = (
            select(cls)
            .where(cls.tool_id == tool_id)
            .options(selectinload(cls.sub_tools))
        )

        result = await db_session.execute(statement)

        instance: Tool | None = result.scalars().first()

        return instance

    # Find mutiple tools their ids.
    @classmethod
    async def find_multiple_by_id(cls, db_session, tool_ids):
        statement = (
            select(cls)
            .filter(cls.tool_id.in_(tool_ids))
            .options(selectinload(cls.sub_tools))
        )

        result = await db_session.execute(statement)
        instances: List[Tool] = result.scalars().all()
        return instances

    @classmethod
    async def find_by_sub_tool_id(cls, db_session, sub_tool_id):
        sub_tool_subquery = (
            select(SubTool.tool_id)
            .where(SubTool.sub_tool_id == sub_tool_id)
            .as_scalar()
        )

        statement = (
            select(cls)
            .where(cls.tool_id == sub_tool_subquery)
            .options(selectinload(cls.sub_tools))
        )
        result = await db_session.execute(statement)
        instance: Tool | None = result.scalars().first()

        return instance

    @classmethod
    async def search_tools(cls, db_session: AsyncSession, search: str):
        statement = (
            select(cls)
            .options(selectinload(cls.sub_tools))
            .where(
                or_(
                    cls.tool_name.ilike(f"%{search}%"),
                    cls.tool_desc.ilike(f"%{search}%"),
                    SubTool.sub_tool_name.ilike(f"%{search}%"),
                )
            )
        )
        result = await db_session.execute(statement)
        instance: List[Tool] = list(result.scalars().all())

        return instance


class SubTool(Base):
    __tablename__ = "sub_tool"

    sub_tool_id: Mapped[str] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    sub_tool_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, unique=True
    )
    sub_tool_description: Mapped[str] = mapped_column(String(5000), nullable=False)
    sub_tool_initial_prompt: Mapped[str] = mapped_column(String(10000), nullable=False)
    sub_tool_image: Mapped[str] = mapped_column(String(200), nullable=False)

    is_archived: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=False
    )
    is_premium: Mapped[bool] = mapped_column(server_default=false(), nullable=False)
    # foreign key that is attached main tool.
    tool_id: Mapped[UUID | None] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("tool.tool_id"), nullable=True
    )

    llm_model: Mapped[str] = mapped_column(
        String(100),
        server_default=LLMModels.MISTRAL.value,
        nullable=False,
    )
    tool: Mapped["Tool"] = relationship("Tool", back_populates="sub_tools")
    score: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    total_messages: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )

    # Get all the sub_tools from the database
    @classmethod
    async def find_sub_tool(cls, db_session: AsyncSession, sub_tool_name: str):
        statement = select(cls).where((cls.sub_tool_name == sub_tool_name))

        result = await db_session.execute(statement)

        instance: SubTool | None = result.scalars().first()

        return instance

    @classmethod
    async def find_multiple_sub_tools(cls, db_session: AsyncSession, sub_tool_names):
        statement = select(cls).filter(cls.sub_tool_name.in_(sub_tool_names))

        result = await db_session.execute(statement)

        instances = result.scalars().all()
        instances = [subtool.sub_tool_name for subtool in instances]

        return instances

    @classmethod
    async def find_by_id(cls, db_session: AsyncSession, sub_tool_id: UUID):
        statement = select(cls).where(
            (cls.sub_tool_id == sub_tool_id) & ~cls.is_archived
        )

        result = await db_session.execute(statement)

        instance: SubTool | None = result.scalars().first()

        return instance

    @classmethod
    async def find_multiple_by_id(cls, db_session: AsyncSession, sub_tool_ids):
        statement = select(cls).filter(cls.sub_tool_id.in_(sub_tool_ids))

        result = await db_session.execute(statement)

        instances: List[SubTool] = result.scalars().all()

        return instances

    @classmethod
    async def get_all(cls, db_session: AsyncSession, isArchived: bool = False):
        if isArchived:
            statement = (
                select(cls).options(selectinload(cls.tool)).filter(cls.is_archived)
            )
        else:
            statement = (
                select(cls).options(selectinload(cls.tool)).filter(~cls.is_archived)
            )

        result = await db_session.execute(statement)

        instances: List[SubTool] = result.scalars().all()

        return instances

    @classmethod
    async def get_all_admin_paginated(
        cls,
        db_session: AsyncSession,
        order_by_clause,
        sub_tool_name: str,
        offset: int = 0,
        limit: int = 10,
        is_archived: bool = False,
    ):
        stmt = (
            select(cls)
            .options(selectinload(cls.tool))
            .where(
                and_(
                    cls.is_archived == is_archived,
                    cls.sub_tool_name.ilike(f"%{sub_tool_name}%"),
                )
            )
        )

        def transform(subtools: [SubTool]):
            return [
                SubToolOutAddInfo(
                    sub_tool_id=subtool.tool_id,
                    sub_tool_name=subtool.sub_tool_name,
                    sub_tool_description=subtool.sub_tool_description,
                    is_premium=subtool.is_premium,
                    sub_tool_initial_prompt=subtool.sub_tool_initial_prompt,
                    sub_tool_image=subtool.sub_tool_image,
                    tool_id=subtool.tool_id,
                    tool=ToolCreateOut(
                        tool_id=subtool.tool_id,
                        tool_name=subtool.tool.tool_name,
                        tool_desc=subtool.tool.tool_desc,
                        is_premium=subtool.tool.is_premium,
                        tool_image=subtool.tool.tool_image,
                        default_color=subtool.tool.default_color,
                    ),
                )
                for subtool in subtools
            ]

        return await paginate_response(
            statement=stmt,
            db_session=db_session,
            model=SubToolOutAddInfo,
            transformer=transform,
            offset=offset,
            limit=limit,
            sorting_attribute=order_by_clause,
            to_orm=True,
        )
