from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import select, or_
from app.routers.api_v1.Service.schemas import Paginate
from app.routers.api_v1.chat.exceptions import (
    EMPTY_PERSONA_ID_AND_TOOL_ID,
    PERSONA_ID_AND_TOOL_ID_BOTH_FILLED,
)
from app.routers.api_v1.Tools.exceptions import TOOL_NOT_FOUND
from app.exceptions import UnprocessableEntityHTTPException
from app.routers.api_v1.Tools.models import SubTool
from app.routers.api_v1.Explore.service import (
    get_discover,
    get_entities,
    get_personas_paginated,
    get_recommended,
    get_subtools_paginated,
    update_total_chat_messages,
)
from app.routers.api_v1.Explore.schemas import EntityCategories, EntityOut, EntityType
from app.routers.api_v1.Auth.models import PreferablePersona, User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.routers.api_v1.Auth.dependencies import (
    get_activated_user,
    is_admin_user,
)
from app.routers.api_v1.Persona.exceptions import (
    PERSONA_NOT_FOUND,
)
from app.routers.api_v1.Persona.models import (
    Persona,
)

explore_router = APIRouter(prefix="/explore", tags=["Explore"])


@explore_router.get("/get_tags", response_model=EntityCategories, status_code=200)
async def get_tags(
    user: User = Depends(get_activated_user),
    db_session: AsyncSession = Depends(get_db),
):
    # TODO: add tags to the database
    add_tags = [
        {
            "title": "Recommended",
            "description": "Suggestions based on your favorite characters",
        },
        {
            "title": "Featured",
            "description": "Best curated Personas and Tools",
        },
        {
            "title": "Discover",
            "description": "Explore new personas and Tools",
        },
        {
            "title": "Tool",
            "description": "Tools",
        },
        {
            "title": "Favorite",
            "description": "Your favorite collections",
        },
    ]

    # get all the distinct persona types from database
    query = (
        select(Persona.persona_type)
        .where(
            or_(
                Persona.creator_uuid == user.id,
                Persona.visible,
            ),
            Persona.is_active,
            ~Persona.is_archived,
        )
        .distinct()
        .order_by(Persona.persona_type.asc())
    )
    result = await db_session.execute(query)
    instance: List[str] = result.scalars().all()

    # convert instance to json

    all_tags = add_tags + list(
        map(lambda title: {"title": title, "description": ""}, instance)
    )

    # TODO: convert to title and description json
    return {"categories": all_tags}


@explore_router.get(
    "/get_by_tag",
    response_model=Paginate[EntityOut],
    response_description="Get all entities by category",
)
async def get_entity_by_tag(
    tag: Annotated[str, Query()] = "Recommended",
    search_query: Annotated[str, Query()] = "",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    if tag == "Tool":
        return await get_subtools_paginated(
            user_id=user.id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            search_query=search_query,
        )

    elif tag == "Featured":
        return await get_entities(
            user_id=user.id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            tag="Featured",
            search_query=search_query,
        )

    elif tag == "Favorite":
        return await get_entities(
            user_id=user.id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            tag="Favorite",
            search_query=search_query,
        )

    elif tag == "Recommended":
        return await get_recommended(
            user_id=user.id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            search_query=search_query,
        )

    elif tag == "Discover":
        return await get_discover(
            user_id=user.id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            search_query=search_query,
        )

    else:
        return await get_personas_paginated(
            user_id=user.id,
            db_session=db_session,
            persona_types={tag},
            limit=limit,
            offset=offset,
            search_query=search_query,
        )


# toggle preferable entity
@explore_router.post(
    "/toggle_preferable_entity", status_code=201, response_model=dict[str, str]
)
async def toggle_preferable_entity(
    user: Annotated[User, Depends(get_activated_user)],
    persona_id: Annotated[UUID, Body(embed=True)] = None,
    tool_id: Annotated[UUID, Body(embed=True)] = None,
    db_session: AsyncSession = Depends(get_db),
):
    if persona_id is None and tool_id is None:
        raise EMPTY_PERSONA_ID_AND_TOOL_ID
    if persona_id is not None and tool_id is not None:
        raise PERSONA_ID_AND_TOOL_ID_BOTH_FILLED

    entity_id = persona_id if persona_id else tool_id
    try:
        if persona_id:
            # check if the persona exists
            db_persona: Persona | None = await Persona.find_by_id(
                db_session=db_session, persona_id=persona_id, user=user
            )
            if not db_persona:
                raise PERSONA_NOT_FOUND

        elif tool_id:
            # check if the tool exists
            db_tool: SubTool | None = await SubTool.find_by_id(
                db_session=db_session, sub_tool_id=tool_id
            )
            if not db_tool:
                raise TOOL_NOT_FOUND

        db_preferable_entity: PreferablePersona | None = (
            await PreferablePersona.find_by_user_id_and_persona_id(
                db_session=db_session, user_id=user.id, persona_id=entity_id
            )
        )

        if db_preferable_entity:
            await db_session.delete(db_preferable_entity)
            await db_session.commit()
            return {"message": "Preferable entity deleted successfully"}
        else:
            db_preferable_entity = PreferablePersona(
                user_id=user.id, persona_id=entity_id
            )
            db_session.add(db_preferable_entity)
            await db_session.commit()
            return {"message": "Preferable entity added successfully"}

    except SQLAlchemyError as ex:
        await db_session.rollback()
        raise UnprocessableEntityHTTPException(msg=repr(ex)) from ex


@explore_router.get(
    "/search",
    response_model=Paginate[EntityOut],
    response_description="Search Personas and Tools",
)
async def search_entities(
    search_query: Annotated[str, Query()] = "",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    return await get_entities(
        user_id=user.id,
        limit=limit,
        offset=offset,
        db_session=db_session,
        tag="Featured",
        search_query=search_query,
    )


# update total messages
@explore_router.put(
    "/update_total_messages",
    status_code=201,
)
async def update_total_messages(
    user: Annotated[User, Depends(is_admin_user)],
    db_session: AsyncSession = Depends(get_db),
):
    try:
        await update_total_chat_messages(db_session=db_session)
        return {"message": "Total Messages Updated Successfully"}
    except:
        return {"message": "Updating Messages Updated Failed"}
