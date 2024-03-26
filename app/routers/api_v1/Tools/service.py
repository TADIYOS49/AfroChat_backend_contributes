from app.routers.api_v1.Tools.exceptions import SUB_TOOL_NOT_FOUND, TOOL_DOES_NOT_EXIST
from app.routers.api_v1.Tools.models import SubTool, Tool
from app.routers.api_v1.Tools.schemas import SubToolEdit, ToolEdit
from sqlalchemy.ext.asyncio import AsyncSession


async def update_tool(db_session: AsyncSession, new_tool: ToolEdit):
    db_tool: Tool | None = await Tool.find_by_id(
        db_session=db_session, tool_id=new_tool.tool_id
    )
    if not db_tool:
        raise TOOL_DOES_NOT_EXIST

    if new_tool.tool_name:
        db_tool.tool_name = new_tool.tool_name

    if new_tool.tool_desc:
        db_tool.tool_desc = new_tool.tool_desc

    if new_tool.tool_image:
        db_tool.tool_image = new_tool.tool_image

    if new_tool.default_color:
        db_tool.default_color = new_tool.default_color

    await db_tool.save(db_session)
    return db_tool


async def update_sub_tool(db_session: AsyncSession, new_sub_tool: SubToolEdit):
    db_sub_tool: SubTool | None = await SubTool.find_by_id(
        db_session=db_session,
        sub_tool_id=new_sub_tool.sub_tool_id,
    )
    if not db_sub_tool:
        raise SUB_TOOL_NOT_FOUND

    if new_sub_tool.tool_id:
        db_sub_tool.tool_id = new_sub_tool.tool_id

    if new_sub_tool.sub_tool_name:
        db_sub_tool.sub_tool_name = new_sub_tool.sub_tool_name

    if new_sub_tool.sub_tool_description:
        db_sub_tool.sub_tool_description = new_sub_tool.sub_tool_description

    if new_sub_tool.sub_tool_image:
        db_sub_tool.sub_tool_image = new_sub_tool.sub_tool_image

    if new_sub_tool.sub_tool_initial_prompt:
        db_sub_tool.sub_tool_initial_prompt = new_sub_tool.sub_tool_initial_prompt

    await db_sub_tool.save(db_session)
    return db_sub_tool
