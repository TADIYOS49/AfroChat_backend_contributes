from typing import List, Annotated
from uuid import UUID
from app.routers.api_v1.Service.schemas import Paginate

from fastapi import APIRouter, Depends, Body, Path, Query
from app.routers.api_v1.Tools.service import update_sub_tool, update_tool
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.api_v1.Tools.exceptions import (
    SUB_TOOL_NOT_FOUND,
    TOOL_NAME_ALREADY_EXIST,
    SUB_TOOL_NAME_ALREADY_EXIST,
    TOOL_DOES_NOT_EXIST,
    TOOL_NOT_FOUND,
)
from app.routers.api_v1.Tools.schemas import (
    SubToolEdit,
    SubToolMulipleCreate,
    SubToolOrderBy,
    ToolCreate,
    SubToolCreate,
    ToolEdit,
    ToolOrderBy,
    ToolOut,
    SubToolOut,
    SubToolOutAddInfo,
    ToolCreateOut,
)
from .models import Tool, SubTool
from ..Auth.dependencies import get_activated_user, is_admin_user
from app.exceptions import BadRequestHTTPException

tool_router = APIRouter(
    prefix="/tool", tags=["Tool"], responses={404: {"description": "Not Found"}}
)


@tool_router.get(
    "/get_all", response_model=List[ToolOut], dependencies=[Depends(get_activated_user)]
)
async def get_all_tools(
    db_session: AsyncSession = Depends(get_db), isArchived: bool = False
):
    tools: List[Tool] = await Tool.get_all(db_session, isArchived=isArchived)

    return tools


@tool_router.get(
    "/get_all_admin",
    response_model=Paginate[ToolOut],
    dependencies=[Depends(is_admin_user)],
)
async def get_all_tools_admin(
    order_by: ToolOrderBy = ToolOrderBy.TOOL_NAME_ASC,
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    tool_name: Annotated[str, Query()] = "",
    is_archived: bool = False,
):
    # Map the ToolOrderBy enum values to the corresponding columns in the database
    order_by_mapping = {
        ToolOrderBy.TOOL_NAME_ASC: Tool.tool_name.asc(),
        ToolOrderBy.TOOL_NAME_DESC: Tool.tool_name.desc(),
    }

    # Get the SQLAlchemy order_by clause based on the user's choice
    order_by_clause = order_by_mapping.get(order_by, Tool.tool_name.asc())

    return await Tool.get_all_admin_paginated(
        db_session,
        order_by_clause=order_by_clause,
        offset=offset,
        limit=limit,
        is_archived=is_archived,
        tool_name=tool_name,
    )


@tool_router.get(
    "/get_all_sub_tools",
    response_model=Paginate[SubToolOutAddInfo],
    dependencies=[Depends(is_admin_user)],
)
async def get_all_sub_tools(
    order_by: SubToolOrderBy = SubToolOrderBy.SUB_TOOL_NAME_ASC,
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    sub_tool_name: Annotated[str, Query()] = "",
    is_archived: bool = False,
    db_session: AsyncSession = Depends(get_db),
):
    # Map the SubToolOrderBy enum values to the corresponding columns in the database
    order_by_mapping = {
        SubToolOrderBy.SUB_TOOL_NAME_ASC: SubTool.sub_tool_name.asc(),
        SubToolOrderBy.SUB_TOOL_NAME_DESC: SubTool.sub_tool_name.desc(),
        SubToolOrderBy.TOOL_NAME_ASC: Tool.tool_name.asc(),
        SubToolOrderBy.TOOL_NAME_DESC: Tool.tool_name.desc(),
    }

    # Get the SQLAlchemy order_by clause based on the user's choice
    order_by_clause = order_by_mapping.get(order_by, SubTool.sub_tool_name.asc())

    return await SubTool.get_all_admin_paginated(
        db_session,
        order_by_clause=order_by_clause,
        offset=offset,
        limit=limit,
        is_archived=is_archived,
        sub_tool_name=sub_tool_name,
    )


@tool_router.get(
    "/get_tool_by_id{tool_id}",
    response_model=ToolOut,
    dependencies=[Depends(get_activated_user)],
)
async def get_tool_by_tool_id(
    tool_id: UUID, db_session: AsyncSession = Depends(get_db)
):
    tool = await Tool.find_by_id(db_session=db_session, tool_id=tool_id)
    if not tool or not tool.is_active:
        raise TOOL_NOT_FOUND
    return tool


@tool_router.delete(
    "/delete_tool{tool_id}",
    response_model=object,
    dependencies=[Depends(is_admin_user)],
)
async def delete_tool(tool_id: UUID, db_session: AsyncSession = Depends(get_db)):
    tool = await Tool.find_by_id(db_session=db_session, tool_id=tool_id)
    if not tool:
        raise TOOL_NOT_FOUND
    tool.is_active = False
    await tool.save(db_session=db_session)
    return {"message": "tool deleted successfully"}


@tool_router.get(
    "/get_sub_tool_by_id{sub_tool_id}",
    response_model=SubToolOut,
    dependencies=[Depends(get_activated_user)],
)
async def get_sub_tool_by_id(
    sub_tool_id: UUID, db_session: AsyncSession = Depends(get_db)
):
    sub_tool = await SubTool.find_by_id(db_session=db_session, sub_tool_id=sub_tool_id)
    if not sub_tool:
        raise SUB_TOOL_NOT_FOUND
    return sub_tool


@tool_router.post(
    "/create", response_model=ToolCreateOut, dependencies=[Depends(is_admin_user)]
)
async def create_tool(
    new_tool: Annotated[ToolCreate, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    db_tool: Tool | None = await Tool.find_by_name(
        db_session=db_session, tool_name=new_tool.tool_name
    )
    if db_tool:
        raise TOOL_NAME_ALREADY_EXIST
    db_new_tool: Tool = Tool(
        tool_name=new_tool.tool_name,
        tool_desc=new_tool.tool_desc,
        tool_image=new_tool.tool_image,
        default_color=new_tool.default_color,
    )
    await db_new_tool.save(db_session)
    return db_new_tool


@tool_router.put(
    "/update_tool", response_model=ToolCreateOut, dependencies=[Depends(is_admin_user)]
)
async def edit_tool(
    new_tool: Annotated[ToolEdit, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    db_tool = await update_tool(db_session=db_session, new_tool=new_tool)
    return db_tool


@tool_router.put(
    "/update_sub_tool", response_model=SubToolOut, dependencies=[Depends(is_admin_user)]
)
async def edit_sub_tool(
    new_sub_tool: Annotated[SubToolEdit, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    db_tool = await update_sub_tool(db_session=db_session, new_sub_tool=new_sub_tool)
    return db_tool


@tool_router.post(
    "/create_sub_tool",
    response_model=SubToolOut,
    dependencies=[Depends(is_admin_user)],
)
async def create_sub_tool(
    new_sub_tool: Annotated[SubToolCreate, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    sub_tool_exist: SubTool | None = await SubTool.find_sub_tool(
        db_session, new_sub_tool.sub_tool_name
    )

    if sub_tool_exist:
        raise SUB_TOOL_NAME_ALREADY_EXIST

    tool_exist: Tool | None = await Tool.find_by_id(db_session, new_sub_tool.tool_id)

    if not tool_exist:
        raise TOOL_DOES_NOT_EXIST

    db_new_sub_tool: SubTool = SubTool(**new_sub_tool.model_dump())
    await db_new_sub_tool.save(db_session)

    return db_new_sub_tool


@tool_router.post(
    "/create_multiple_sub_tools",
    response_model=List[SubToolOut],
    dependencies=[Depends(is_admin_user)],
)
async def create_multiple_sub_tools(
    new_sub_tools: SubToolMulipleCreate,
    db_session: AsyncSession = Depends(get_db),
):
    new_sub_tools = new_sub_tools.data
    # Check for existing subtool names
    sub_tool_names = [sub_tool.sub_tool_name for sub_tool in new_sub_tools]
    sub_tools_exist = await SubTool.find_multiple_sub_tools(db_session, sub_tool_names)

    if sub_tools_exist:
        raise BadRequestHTTPException(
            msg=f'{", ".join(sub_tools_exist)} names already exist.'
        )

    # Check for existing tools
    for new_sub_tool in new_sub_tools:
        tool_exist: Tool | None = await Tool.find_by_id(
            db_session, new_sub_tool.tool_id
        )

        if not tool_exist:
            raise TOOL_DOES_NOT_EXIST

    created_sub_tools = []
    for new_sub_tool in new_sub_tools:
        db_new_sub_tool: SubTool = SubTool(**new_sub_tool.model_dump())
        db_session.add(db_new_sub_tool)

        created_sub_tools.append(db_new_sub_tool)

    await db_session.commit()
    return created_sub_tools


@tool_router.get(
    "/search_tools_sub_tools",
    response_model=List[ToolOut],
)
async def search_tools_sub_tools(
    search: Annotated[str, Query()],
    db_session: AsyncSession = Depends(get_db),
):
    tools: List[Tool] = await Tool.search_tools(db_session, search)

    return tools


@tool_router.delete(
    "/delete_subtool{sub_tool_id}",
    response_model=object,
)
async def delete_sub_tool(
    sub_tool_id: Annotated[UUID, Path()],
    db_session: AsyncSession = Depends(get_db),
):
    sub_tool = await SubTool.find_by_id(db_session=db_session, sub_tool_id=sub_tool_id)
    if not sub_tool:
        raise SUB_TOOL_NOT_FOUND

    await sub_tool.delete(db_session=db_session)
    await db_session.commit()

    return {"message": "Sub tool deleted successfully"}


@tool_router.get(
    "/get_tool_by_sub_tool_id/{subtool_id}",
    response_model=ToolOut,
)
async def get_tool_by_sub_tool_id(
    subtool_id: UUID,
    db_session: AsyncSession = Depends(get_db),
):
    # raise
    tool: Tool | None = await Tool.find_by_sub_tool_id(
        db_session=db_session, sub_tool_id=subtool_id
    )

    if not tool:
        raise SUB_TOOL_NOT_FOUND
    return tool
