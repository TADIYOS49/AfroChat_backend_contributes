from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Body, Depends, Path, Query
from app.routers.api_v1.Persona.models import Persona
from app.routers.api_v1.Tools.models import Tool, SubTool
from app.routers.api_v1.Auth.dependencies import is_admin_user
from app.routers.api_v1.Auth.exceptions import (
    USER_NOT_FOUND,
)
from app.routers.api_v1.Auth.models import User, UserEmail
from app.routers.api_v1.Auth.schemas import UserOutAdmin
from app.routers.api_v1.User.exceptions import PERMISSION_NOT_ALLOWED
from app.routers.api_v1.User.schemas import (
    CompleteRegistration,
    UpdateUserProfileAdmin,
    UserCreateAdmin,
    OrderBy,
)
from app.routers.api_v1.User.service import create_new_user, update_user_service
from app.routers.api_v1.Service.schemas import Paginate

from app.routers.api_v1.Persona.exceptions import (
    PERSONA_NOT_FOUND,
)
from app.routers.api_v1.Tools.exceptions import TOOL_NOT_FOUND, SUB_TOOL_NOT_FOUND

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db


admin_crud_router = APIRouter(
    prefix="/admin_crud_router",
    tags=["Admin Management"],
    responses={404: {"description": "Not found"}},
)


@admin_crud_router.get(
    "/get_all",
    response_model=Paginate[UserOutAdmin],
    dependencies=[Depends(is_admin_user)],
)
async def get_all_users(
    order_by: OrderBy,
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    search_query: Annotated[str, Query()] = "",
    db_session: AsyncSession = Depends(get_db),
):
    # Map the OrderBy enum values to the corresponding columns in the database
    order_by_mapping = {
        OrderBy.USERNAME_ASC: User.username.asc(),
        OrderBy.USERNAME_DESC: User.username.desc(),
        OrderBy.ROLE_ASC: User.role.asc(),
        OrderBy.ROLE_DESC: User.role.desc(),
        OrderBy.REGISTRATION_DATE_ASC: User.created_at.asc(),
        OrderBy.REGISTRATION_DATE_DESC: User.created_at.desc(),
    }

    # Get the SQLAlchemy order_by clause based on the user's choice
    order_by_clause = order_by_mapping.get(order_by, User.username.asc())

    return await User.get_all_pagination(
        db_session=db_session,
        limit=limit,
        offset=offset,
        order_by_clause=order_by_clause,
        search=search_query,
    )


@admin_crud_router.get(
    "/get_user_by_id{user_id}",
    response_model=UserOutAdmin,
    dependencies=[Depends(is_admin_user)],
)
async def get_user_by_user_id(
    user_id: UUID, db_session: AsyncSession = Depends(get_db)
):
    db_user = await User.find(db_session=db_session, user_id=user_id)
    if not db_user:
        raise USER_NOT_FOUND

    return UserOutAdmin.from_orm(db_user)


@admin_crud_router.post("/create_user", response_model=UserOutAdmin, status_code=201)
async def create_user(
    creator: Annotated[User, Depends(is_admin_user)],
    new_user: Annotated[UserCreateAdmin, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    db_user = await create_new_user(
        db_session=db_session, new_user=new_user, creator=creator
    )
    return UserOutAdmin.from_orm(db_user)


@admin_crud_router.post(
    "/complete_registration", response_model=UserOutAdmin, status_code=201
)
async def complete_registration(
    complete_registration: Annotated[CompleteRegistration, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    db_user = await User.find_by_email(
        db_session=db_session, email=complete_registration.email
    )
    if not db_user:
        raise USER_NOT_FOUND

    db_user_email = await UserEmail.find(
        db_session=db_session, email=complete_registration.email
    )
    if not db_user_email:
        raise USER_NOT_FOUND
    try:
        db_user_email.is_activated = True
        db_user.is_activated = True
        await db_user.save(db_session=db_session)
        await db_user_email.save(db_session=db_session)
        await db_session.commit()
    except Exception as ex:
        await db_session.rollback()
        raise ex

    return UserOutAdmin.from_orm(db_user)


@admin_crud_router.put(
    "/update_user",
    response_model=UserOutAdmin,
    status_code=201,
)
async def update_user(
    updator: Annotated[User, Depends(is_admin_user)],
    new_user: Annotated[UpdateUserProfileAdmin, Body()],
    db_session: AsyncSession = Depends(get_db),
):
    db_user = await update_user_service(
        db_session=db_session, new_user=new_user, updator=updator
    )
    return UserOutAdmin.from_orm(db_user)


@admin_crud_router.post(
    "/archive_user{user_id}", response_model=object, status_code=201
)
async def archive_user(
    admin_user: Annotated[User, Depends(is_admin_user)],
    user_id: Annotated[UUID, Path()],
    db_session: AsyncSession = Depends(get_db),
):
    db_user = await User.find(db_session=db_session, user_id=user_id)
    if not db_user:
        raise USER_NOT_FOUND

    if db_user.role >= admin_user.role:
        raise PERMISSION_NOT_ALLOWED

    db_user.is_archived = not db_user.is_archived
    await db_user.save(db_session)

    if db_user.is_archived:
        return {"message": "successfully archived user"}
    else:
        return {"message": "user successfully removed from archive"}


@admin_crud_router.post(
    "/archive_multiple_users", response_model=object, status_code=201
)
async def archive_multiple_users(
    admin_user: Annotated[User, Depends(is_admin_user)],
    user_ids: List[UUID] = Body(..., embed=True),
    db_session: AsyncSession = Depends(get_db),
):
    db_users = await User.find_multiple(db_session=db_session, user_ids=user_ids)

    if len(user_ids) != len(db_users):
        raise USER_NOT_FOUND

    for db_user in db_users:
        if db_user.role >= admin_user.role:
            raise PERMISSION_NOT_ALLOWED

    for db_user in db_users:
        db_user.is_archived = not db_user.is_archived

    await db_user.save(db_session)

    if db_users[0].is_archived:
        return {"message": "successfully archived users"}
    else:
        return {"message": "Users successfully removed from archive"}


@admin_crud_router.delete(
    "/delete_user{user_id}", response_model=object, status_code=201
)
async def delete_user(
    admin_user: Annotated[User, Depends(is_admin_user)],
    user_id: Annotated[UUID, Path()],
    db_session: AsyncSession = Depends(get_db),
):
    db_user = await User.find(db_session=db_session, user_id=user_id)
    if not db_user:
        raise USER_NOT_FOUND

    if db_user.role >= admin_user.role:
        raise PERMISSION_NOT_ALLOWED

    await db_user.delete(db_session)
    return {"message": "successfully archived user"}


@admin_crud_router.post(
    "/archive_persona{persona_id}", response_model=object, status_code=201
)
async def archive_persona(
    admin_user: Annotated[User, Depends(is_admin_user)],
    persona_id: Annotated[UUID, Path()],
    db_session: AsyncSession = Depends(get_db),
):
    db_persona: Persona | None = await Persona.find_by_id(
        db_session=db_session, persona_id=persona_id, user=admin_user
    )

    if not db_persona:
        raise PERSONA_NOT_FOUND

    db_persona.is_active = not db_persona.is_active
    await db_persona.save(db_session)

    if db_persona.is_active:
        return {"message": "successfully archived persona"}
    else:
        return {"message": "persona successfully removed from archive"}


@admin_crud_router.post(
    "/archive_multiple_personas", response_model=object, status_code=201
)
async def archive_multiple_personas(
    admin_user: Annotated[User, Depends(is_admin_user)],
    persona_ids: List[UUID] = Body(..., embed=True),
    db_session: AsyncSession = Depends(get_db),
):
    db_personas = await Persona.find_multiple_by_id(
        db_session=db_session, persona_ids=persona_ids
    )

    if len(persona_ids) != len(db_personas):
        raise PERSONA_NOT_FOUND

    for db_persona in db_personas:
        db_persona.is_active = not db_persona.is_active

    await db_persona.save(db_session)

    if db_personas[0].is_active:
        return {"message": "successfully archived personas"}
    else:
        return {"message": "personas successfully removed from archive"}


@admin_crud_router.post(
    "/archive_tool{tool_id}", response_model=object, status_code=201
)
async def archive_tool(
    admin_user: Annotated[User, Depends(is_admin_user)],
    tool_id: Annotated[UUID, Path()],
    db_session: AsyncSession = Depends(get_db),
):
    db_tool: Tool | None = await Tool.find_by_id(db_session=db_session, tool_id=tool_id)
    if not db_tool:
        raise TOOL_NOT_FOUND

    db_tool.is_active = not db_tool.is_active
    for db_subtool in db_tool.sub_tools:
        db_subtool.is_archived = not db_tool.is_active

    await db_tool.save(db_session)
    if db_tool.is_active:
        return {"message": "successfully archived tool and its subtools"}
    else:
        return {"message": "tool and its subtools successfully removed from archive"}


@admin_crud_router.post(
    "/archive_multiple_tools", response_model=object, status_code=201
)
async def archive_multiple_tools(
    admin_user: Annotated[User, Depends(is_admin_user)],
    tool_ids: List[UUID] = Body(..., embed=True),
    db_session: AsyncSession = Depends(get_db),
):
    db_tools = await Tool.find_multiple_by_id(db_session=db_session, tool_ids=tool_ids)

    if len(tool_ids) != len(db_tools):
        raise TOOL_NOT_FOUND

    for db_tool in db_tools:
        db_tool.is_active = not db_tool.is_active

        for db_subtool in db_tool.sub_tools:
            db_subtool.is_archived = not db_tool.is_active

    await db_tool.save(db_session)
    if db_tools[0].is_active:
        return {"message": "successfully archived tools"}
    else:
        return {"message": "tools successfully removed from archive"}


@admin_crud_router.post(
    "/archive_sub_tool{sub_tool_id}", response_model=object, status_code=201
)
async def archive_sub_tool(
    admin_user: Annotated[User, Depends(is_admin_user)],
    sub_tool_id: Annotated[UUID, Path()],
    db_session: AsyncSession = Depends(get_db),
):
    db_sub_tool: SubTool | None = await SubTool.find_by_id(
        db_session=db_session, sub_tool_id=sub_tool_id
    )
    if not db_sub_tool:
        raise SUB_TOOL_NOT_FOUND

    db_sub_tool.is_archived = not db_sub_tool.is_archived
    await db_sub_tool.save(db_session)

    if db_sub_tool.is_archived:
        return {"message": "successfully archived subtool"}
    else:
        return {"message": "Subtool successfully removed from archive"}


@admin_crud_router.post(
    "/archive_multiple_subtools", response_model=object, status_code=201
)
async def archive_multiple_subtools(
    admin_user: Annotated[User, Depends(is_admin_user)],
    sub_tool_ids: List[UUID] = Body(..., embed=True),
    db_session: AsyncSession = Depends(get_db),
):
    db_sub_tools = await SubTool.find_multiple_by_id(
        db_session=db_session, sub_tool_ids=sub_tool_ids
    )

    if len(sub_tool_ids) != len(db_sub_tools):
        raise SUB_TOOL_NOT_FOUND

    for db_sub_tool in db_sub_tools:
        db_sub_tool.is_archived = not db_sub_tool.is_archived

    await db_sub_tool.save(db_session)
    if db_sub_tools[0].is_archived:
        return {"message": "successfully archived subtools"}
    else:
        return {"message": "subtools successfully removed from archive"}
