from collections import Counter
from typing import Annotated, List
from uuid import UUID

from sqlalchemy import case, func, join, literal, or_, select, update
from app.routers.api_v1.chat.models import ChatMessage, ChatSession
from app.routers.api_v1.Persona.models import Persona
from app.routers.api_v1.Auth.models import PreferablePersona, User
from app.routers.api_v1.Service.utils import paginate_response
from app.routers.api_v1.Explore.schemas import EntityOut
from app.routers.api_v1.Tools.models import SubTool, Tool

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from sqlalchemy.orm import selectinload


async def get_entities(
    user_id: UUID,
    tag: str,
    search_query="",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
):
    if tag == "Featured":
        personas_paginated = await get_personas_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            search_query=search_query,
        )
        subtools_paginated = await get_subtools_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            search_query=search_query,
        )

    if tag == "Favorite":
        personas_paginated = await get_preferable_personas(
            user_id=user_id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            search_query=search_query,
        )
        subtools_paginated = await get_preferable_subtools(
            user_id=user_id,
            limit=limit,
            offset=offset,
            db_session=db_session,
            search_query=search_query,
        )

    combined_results = personas_paginated.data + subtools_paginated.data

    # Combine the metadata
    total = personas_paginated.meta_data.total + subtools_paginated.meta_data.total
    returned = (
        personas_paginated.meta_data.returned + subtools_paginated.meta_data.returned
    )
    max_value = max(
        personas_paginated.meta_data.max_value, subtools_paginated.meta_data.max_value
    )

    combined_meta_data = {
        "total": total,
        "offset": offset,
        "limit": limit,
        "returned": returned,
        "max_value": max_value,
    }

    return {"data": combined_results, "meta_data": combined_meta_data}


async def get_recommended(
    user_id: UUID,
    search_query="",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
):
    personas_paginated = await get_recommended_personas(
        user_id=user_id,
        limit=limit,
        offset=offset,
        db_session=db_session,
        search_query=search_query,
    )

    subtools_paginated = await get_recommended_subtools(
        user_id=user_id,
        limit=limit,
        offset=offset,
        db_session=db_session,
        search_query=search_query,
    )

    combined_results = personas_paginated.data + subtools_paginated.data

    # Combine the metadata
    total = personas_paginated.meta_data.total + subtools_paginated.meta_data.total
    returned = (
        personas_paginated.meta_data.returned + subtools_paginated.meta_data.returned
    )
    max_value = max(
        personas_paginated.meta_data.max_value, subtools_paginated.meta_data.max_value
    )

    combined_meta_data = {
        "total": total,
        "offset": offset,
        "limit": limit,
        "returned": returned,
        "max_value": max_value,
    }

    return {"data": combined_results, "meta_data": combined_meta_data}


async def get_recommended_personas(
    user_id: UUID,
    search_query="",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(ChatSession.id, ChatSession.persona_id, Persona.persona_type)
        .join(Persona)
        .where(
            ChatSession.user_id == user_id,
            Persona.is_active,
            ~Persona.is_archived,
        )
    )
    result = await db_session.execute(stmt)
    instances = result.fetchall()

    unique_combinations = {
        (chat_session_id, persona_id, persona_type)
        for chat_session_id, persona_id, persona_type in instances
    }

    # Extracting persona IDs and persona types from unique combinations
    persona_ids = {persona_id for _, persona_id, _ in unique_combinations}
    persona_types = [persona_type for _, _, persona_type in unique_combinations]

    # Counting the occurrences of each persona_type
    persona_type_counts = Counter(persona_types)

    query = (
        select(Persona.persona_type)
        .where(
            or_(
                Persona.creator_uuid == user_id,
                Persona.visible,
            ),
            Persona.is_active,
            ~Persona.is_archived,
        )
        .distinct()
    )
    result = await db_session.execute(query)
    instances: List[str] = result.scalars().all()

    for persona_type in instances:
        if persona_type not in persona_types:
            persona_type_counts[persona_type] = 0

    # Sorting categories based on their count
    ordered_persona_types = sorted(
        persona_type_counts.keys(), key=lambda x: persona_type_counts[x], reverse=True
    )

    # Dynamically construct the order_by clause based on ordered_persona_types
    order_by_clause = case(
        {
            persona_type: index
            for index, persona_type in enumerate(ordered_persona_types)
        },
        value=Persona.persona_type,
    )

    return await get_personas_paginated(
        user_id=user_id,
        db_session=db_session,
        persona_types=ordered_persona_types,
        persona_ids=persona_ids,
        limit=limit,
        offset=offset,
        search_query=search_query,
        order_by_clause=order_by_clause,
    )


async def get_recommended_subtools(
    user_id: UUID,
    search_query="",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(ChatSession.id, ChatSession.sub_tool_id, Tool.tool_name)
        .select_from(
            join(
                ChatSession, SubTool, ChatSession.sub_tool_id == SubTool.sub_tool_id
            ).join(Tool, SubTool.tool_id == Tool.tool_id)
        )
        .where(ChatSession.user_id == user_id)
    )

    result = await db_session.execute(stmt)
    instances = result.fetchall()

    unique_combinations = {
        (chat_session_id, subtool_id, tool_name)
        for chat_session_id, subtool_id, tool_name in instances
    }

    # Extracting persona IDs and persona types from unique combinations
    subtool_ids = {subtool_id for _, subtool_id, _ in unique_combinations}
    tool_names = [tool_name for _, _, tool_name in unique_combinations]

    tool_name_counts = Counter(tool_names)

    query = select(Tool.tool_name)
    result = await db_session.execute(query)
    instances: List[str] = result.scalars().all()

    for tool_name in instances:
        if tool_name not in tool_name_counts:
            tool_name_counts[tool_name] = 0

    # Sorting categories based on their count
    ordered_tool_names = sorted(
        tool_name_counts.keys(), key=lambda x: tool_name_counts[x], reverse=True
    )

    # Dynamically construct the order_by clause based on tool_names
    order_by_clause = case(
        {tool_name: index for index, tool_name in enumerate(ordered_tool_names)},
        value=Tool.tool_name,
    )

    return await get_subtools_paginated(
        user_id=user_id,
        db_session=db_session,
        tool_names=ordered_tool_names,
        subtool_ids=subtool_ids,
        limit=limit,
        offset=offset,
        search_query=search_query,
        order_by_clause=order_by_clause,
    )


async def get_discover(
    user_id: UUID,
    search_query="",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
):
    # Retrieve Persona ids used by user
    stmt_persona = select(ChatSession.persona_id).where(ChatSession.user_id == user_id)

    result_persona = await db_session.execute(stmt_persona)
    instances = result_persona.fetchall()
    persona_ids = {instance[0] for instance in instances if instance[0] is not None}

    # Retrieve Subtools used by user
    stmt_subtool = select(ChatSession.sub_tool_id).where(ChatSession.user_id == user_id)

    result_subtool = await db_session.execute(stmt_subtool)
    instances = result_subtool.fetchall()
    subtool_ids = {instance[0] for instance in instances if instance[0] is not None}

    # Retrieve most popular personas and subtools not used by user
    personas_paginated = await get_personas_paginated(
        user_id=user_id,
        limit=limit,
        offset=offset,
        db_session=db_session,
        order_by_clause=Persona.total_messages.desc(),
        persona_ids=persona_ids,
        search_query=search_query,
    )

    subtools_paginated = await get_subtools_paginated(
        user_id=user_id,
        limit=limit,
        offset=offset,
        db_session=db_session,
        order_by_clause=SubTool.total_messages.desc(),
        subtool_ids=subtool_ids,
        search_query=search_query,
    )

    combined_results = personas_paginated.data + subtools_paginated.data

    # Combine the metadata
    total = personas_paginated.meta_data.total + subtools_paginated.meta_data.total
    returned = (
        personas_paginated.meta_data.returned + subtools_paginated.meta_data.returned
    )
    max_value = max(
        personas_paginated.meta_data.max_value, subtools_paginated.meta_data.max_value
    )

    combined_meta_data = {
        "total": total,
        "offset": offset,
        "limit": limit,
        "returned": returned,
        "max_value": max_value,
    }

    return {"data": combined_results, "meta_data": combined_meta_data}


async def get_personas_paginated(
    user_id: UUID,
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    order_by_clause=Persona.score.desc(),
    search_query="",
    persona_types=[],
    persona_ids=set(),
):
    subquery = (
        select(
            func.max(
                case(
                    (
                        (
                            PreferablePersona.user_id == user_id,
                            1,
                        )
                    ),
                    else_=0,
                )
            ).label("is_preferable_persona")
        )
        .where(PreferablePersona.persona_id == Persona.id)
        .scalar_subquery()
    )

    query = (
        select(Persona, func.coalesce(subquery, 0).label("is_preferable_persona"))
        .options(selectinload(Persona.creator))
        .where(
            Persona.visible,
            Persona.is_active,
            ~Persona.is_archived,
            ~Persona.id.in_(persona_ids),
            Persona.full_name.ilike(f"%{search_query}%"),
        )
    )

    if len(persona_types) > 0:
        query = query.where(Persona.persona_type.in_(persona_types))

    def transform_personas(personas):
        return [
            EntityOut(
                id=persona[0].id,
                name=persona[0].full_name,
                image=persona[0].persona_image,
                default_color=persona[0].default_color,
                description=persona[0].description,
                is_premium=persona[0].is_premium,
                creator_uuid=persona[0].creator_uuid,
                created_at=persona[0].created_at,
                created_by=persona[0].creator.username,
                type="Persona",
                is_preferable_entity=persona[1],
                total_messages=persona[0].total_messages,
            )
            for persona in personas
        ]

    return await paginate_response(
        statement=query,
        db_session=db_session,
        model=EntityOut,
        offset=offset,
        limit=limit,
        sorting_attribute=order_by_clause,
        transformer=transform_personas,
    )


async def get_subtools_paginated(
    user_id: UUID,
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    order_by_clause=SubTool.score.desc(),
    search_query="",
    subtool_ids=set(),
    tool_names=[],
):
    subquery = (
        select(
            func.max(
                case(
                    (
                        (
                            PreferablePersona.user_id == user_id,
                            1,
                        )
                    ),
                    else_=0,
                )
            ).label("is_preferable_entity")
        )
        .where(PreferablePersona.persona_id == SubTool.sub_tool_id)
        .scalar_subquery()
    )

    query = select(
        SubTool, func.coalesce(subquery, 0).label("is_preferable_entity")
    ).where(
        ~SubTool.is_archived,
        ~SubTool.sub_tool_id.in_(subtool_ids),
        SubTool.sub_tool_name.ilike(f"%{search_query}%"),
    )

    if len(tool_names) > 0:
        query = query.join(Tool, SubTool.tool_id == Tool.tool_id).where(
            Tool.tool_name.in_(tool_names)
        )

    def transform_subtools(subtools):
        return [
            EntityOut(
                id=subtool[0].sub_tool_id,
                name=subtool[0].sub_tool_name,
                description=subtool[0].sub_tool_description,
                image=subtool[0].sub_tool_image,
                is_premium=subtool[0].is_premium,
                type="Tool",
                is_preferable_entity=subtool[1],
                total_messages=subtool[0].total_messages,
            )
            for subtool in subtools
        ]

    return await paginate_response(
        statement=query,
        db_session=db_session,
        model=EntityOut,
        offset=offset,
        limit=limit,
        sorting_attribute=order_by_clause,
        transformer=transform_subtools,
    )


async def get_preferable_personas(
    user_id: UUID,
    search_query="",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    order_by_clause=Persona.score.desc(),
):
    query = (
        select(Persona)
        .options(selectinload(Persona.creator))
        .where(
            Persona.is_active,
            Persona.visible,
            ~Persona.is_archived,
            Persona.full_name.ilike(f"%{search_query}%"),
        )
        .join(PreferablePersona, Persona.id == PreferablePersona.persona_id)
        .join(User, User.id == PreferablePersona.user_id)
        .where(User.id == user_id)
    )

    def transform_personas(personas):
        return [
            EntityOut(
                id=persona.id,
                name=persona.full_name,
                image=persona.persona_image,
                default_color=persona.default_color,
                description=persona.description,
                is_premium=persona.is_premium,
                creator_uuid=persona.creator_uuid,
                created_at=persona.created_at,
                created_by=persona.creator.username,
                type="Persona",
                is_preferable_entity=True,
                total_messages=persona.total_messages,
            )
            for persona in personas
        ]

    return await paginate_response(
        statement=query,
        db_session=db_session,
        model=EntityOut,
        offset=offset,
        limit=limit,
        sorting_attribute=order_by_clause,
        transformer=transform_personas,
        to_orm=True,
    )


async def get_preferable_subtools(
    user_id: UUID,
    search_query="",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    order_by_clause=SubTool.score.desc(),
):
    query = (
        select(SubTool)
        .where(
            ~SubTool.is_archived,
            SubTool.sub_tool_name.ilike(f"%{search_query}%"),
        )
        .join(PreferablePersona, SubTool.sub_tool_id == PreferablePersona.persona_id)
        .join(User, User.id == PreferablePersona.user_id)
        .where(User.id == user_id)
    )

    def transform_subtools(subtools):
        return [
            EntityOut(
                id=subtool.sub_tool_id,
                name=subtool.sub_tool_name,
                description=subtool.sub_tool_description,
                image=subtool.sub_tool_image,
                is_premium=subtool.is_premium,
                type="Tool",
                is_preferable_entity=True,
                total_messages=subtool.total_messages,
            )
            for subtool in subtools
        ]

    return await paginate_response(
        statement=query,
        db_session=db_session,
        model=EntityOut,
        offset=offset,
        limit=limit,
        sorting_attribute=order_by_clause,
        transformer=transform_subtools,
        to_orm=True,
    )


async def update_total_chat_messages(
    db_session: AsyncSession = Depends(get_db),
):
    await update_total_chat_messages_personas(db_session=db_session)
    await update_total_chat_messages_subtools(db_session=db_session)


async def update_total_chat_messages_personas(
    db_session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(
            ChatSession.persona_id, func.count(ChatMessage.id).label("message_count")
        )
        .select_from(ChatSession)
        .join(ChatMessage, ChatMessage.chat_session_id == ChatSession.id)
        .group_by(ChatSession.persona_id)
    )

    result = await db_session.execute(stmt)
    instances = result.fetchall()

    # Initialize total_messages to zero for all personas, ensuring inclusion of personas with deleted messages
    stmt = update(Persona).values(total_messages=0)
    await db_session.execute(stmt)

    for persona_id, message_count in instances:
        stmt = (
            update(Persona)
            .where(Persona.id == persona_id)
            .values(total_messages=message_count)
        )
        await db_session.execute(stmt)

    await db_session.commit()


async def update_total_chat_messages_subtools(
    db_session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(
            ChatSession.sub_tool_id, func.count(ChatMessage.id).label("message_count")
        )
        .select_from(ChatSession)
        .join(ChatMessage, ChatMessage.chat_session_id == ChatSession.id)
        .group_by(ChatSession.sub_tool_id)
    )

    result = await db_session.execute(stmt)
    instances = result.fetchall()

    # Initialize total_messages to zero for all personas, ensuring inclusion of personas with deleted messages
    stmt = update(SubTool).values(total_messages=0)
    await db_session.execute(stmt)

    for subtool_id, message_count in instances:
        stmt = (
            update(SubTool)
            .where(SubTool.sub_tool_id == subtool_id)
            .values(total_messages=message_count)
        )
        await db_session.execute(stmt)

    await db_session.commit()
