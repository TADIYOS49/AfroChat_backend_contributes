from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query
from app.routers.api_v1.Auth.models import PreferablePersona, User
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.exceptions import UnprocessableEntityHTTPException, NotFoundHTTPException
from app.routers.api_v1.Auth.dependencies import (
    get_activated_user,
    get_persona_number_validated_user,
    is_admin_user,
)
from app.routers.api_v1.Persona.exceptions import (
    PERSONA_NOT_FOUND,
    PERSONA_NAME_ALREADY_EXISTS,
)
from app.routers.api_v1.Persona.models import (
    Persona,
)
from app.routers.api_v1.Persona.schemas import (
    OrderBy,
    PersonaCategories,
    PersonaEdit,
    PersonaExists,
    PersonaOut,
    PersonaCreate,
    OnboardingPersonaOut,
    PersonaOutDiscover,
    PersonaOutNoQuotes,
    PersonasByCategory,
    PersonaOutWithOutQuotes,
    PersonaType,
    PersonaInitialPromptInput,
    PersonaOutWithVisible,
    PersonaEditInitialPromptInput,
)
from app.routers.api_v1.Persona.service import (
    create_new_persona,
    edit_persona,
    edit_persona_for_users,
)
from app.routers.api_v1.Service.schemas import Paginate
from app.routers.api_v1.Persona.service import create_initial_prompt
from app.routers.api_v1.chat.schemas import ChatSessionBaseOutSchema

persona_router = APIRouter(prefix="/persona", tags=["Persona"])


@persona_router.post("/create", response_model=PersonaOut, status_code=201)
async def create_persona(
    persona: Annotated[PersonaCreate, Body()],
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(is_admin_user),
):
    db_persona: Persona | None = await Persona.find_by_full_name(
        db_session=db_session, full_name=persona.full_name
    )
    if db_persona:
        raise PERSONA_NAME_ALREADY_EXISTS

    db_persona = await create_new_persona(
        db_session=db_session, persona=persona, user=user
    )

    return db_persona


@persona_router.get(
    "/check_persona_name", response_model=PersonaExists, status_code=200
)
async def check_persona_name(
    persona_name: str,
    db_session: AsyncSession = Depends(get_db),
):
    db_persona: Persona | None = await Persona.find_by_full_name(
        db_session=db_session, full_name=persona_name
    )
    if db_persona:
        return PersonaExists(exists=True, message="persona name already taken")

    return PersonaExists(exists=False, message="persona name is available")


@persona_router.get(
    "/get_categories", response_model=PersonaCategories, status_code=200
)
async def get_categories():
    return PersonaCategories(categories=[p.value for p in list(PersonaType)])


@persona_router.post("/update", response_model=PersonaOut, status_code=201)
async def update_persona(
    persona: Annotated[PersonaEdit, Body()],
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(is_admin_user),
):
    db_persona: Persona | None = await Persona.find_by_id(
        db_session=db_session, persona_id=persona.id, user=user
    )
    #
    if not db_persona:
        raise PERSONA_NOT_FOUND

    db_persona = await edit_persona(
        db_session=db_session, db_persona=db_persona, new_persona=persona
    )

    return db_persona


@persona_router.get(
    "/get_all",
    response_model=Paginate[PersonaOut],
)
async def get_all_persona(
    order_by: OrderBy,
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    is_archived: bool = False,
    persona_name: Annotated[str, Query()] = "",
    persona_type: Annotated[PersonaType, Query()] | None = None,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    order_by_mapping = {
        OrderBy.PERSONA_NAME_ASC: Persona.full_name.asc(),
        OrderBy.PERSONA_NAME_DESC: Persona.full_name.desc(),
        OrderBy.CATEGORY_ASC: Persona.persona_type.asc(),
        OrderBy.CATEGORY_DESC: Persona.persona_type.desc(),
    }

    # Get the SQLAlchemy order_by clause based on the user's choice
    order_by_clause = order_by_mapping.get(order_by, Persona.full_name.asc())

    return await Persona.search_persona(
        db_session=db_session,
        persona_name=persona_name,
        persona_type=persona_type,
        limit=limit,
        offset=offset,
        is_archived=is_archived,
        order_by_clause=order_by_clause,
        user=user,
    )

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
    )


@persona_router.get(
    "/get_all_by_types",
    response_model=list[PersonasByCategory],
)
async def get_all_persona_by_type(
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    res: List[PersonasByCategory] = []
    for persona_type in PersonaType:
        db_persona: List[PersonaOutNoQuotes] = await Persona.find_by_persona_type2(
            db_session=db_session, persona_type=persona_type, user=user
        )
        res.append(PersonasByCategory(persona_type=persona_type, personas=db_persona))

    return res


@persona_router.get(
    "/get_persona_onboarding", response_model=list[OnboardingPersonaOut]
)
async def get_persona_onboarding(
    db_session: AsyncSession = Depends(get_db),
) -> List[OnboardingPersonaOut]:
    db_personas: List[Persona] = await Persona.get_all(db_session=db_session)

    persona_list: List[OnboardingPersonaOut] = [
        OnboardingPersonaOut(id=db_persona.id, full_name=db_persona.full_name)
        for db_persona in db_personas
    ]

    return persona_list


@persona_router.get(
    "/get_by_id/{id}",
    response_model=PersonaOut,
)
async def get_persona_by_id(
    persona_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    db_persona: Persona | None = await Persona.find_by_id(
        db_session=db_session, persona_id=persona_id, user=user
    )
    # map the preferred persona with the personas based on the user id
    if not db_persona:
        raise PERSONA_NOT_FOUND
    return db_persona


@persona_router.delete(
    "/delete_by_id/{id}",
    response_model=object,
)
async def delete_persona_by_id(
    persona_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(is_admin_user),
):
    db_persona: Persona | None = await Persona.find_by_id(
        db_session=db_session, persona_id=persona_id, user=user
    )
    if not db_persona:
        raise PERSONA_NOT_FOUND

    db_persona.is_active = False
    await db_session.commit()
    return {"message": "Persona deleted successfully"}


@persona_router.get(
    "/get_by_category",
    response_model=Paginate[PersonaOutNoQuotes],
    response_description="Get all personas by category",
)
async def get_persona_by_category(
    category: Annotated[PersonaType, Query()],
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    return await Persona.find_by_persona_type(
        db_session=db_session,
        persona_type=category,
        limit=limit,
        offset=offset,
        user=user,
    )


# add favourite personas
@persona_router.post(
    "/add_favourite_personas", status_code=201, response_model=dict[str, str]
)
async def add_favourite_personas(
    user: Annotated[User, Depends(get_activated_user)],
    persona_ids: List[UUID] = Body(..., embed=True),
    db_session: AsyncSession = Depends(get_db),
):
    try:
        for persona_id in persona_ids:
            # check if the persona exists
            db_persona: Persona | None = await Persona.find_by_id(
                db_session=db_session, persona_id=persona_id, user=user
            )
            if not db_persona:
                raise PERSONA_NOT_FOUND

            db_preferable_persona: PreferablePersona | None = (
                await PreferablePersona.find_by_user_id_and_persona_id(
                    db_session=db_session, user_id=user.id, persona_id=persona_id
                )
            )
            if not db_preferable_persona:
                db_preferable_persona = PreferablePersona(
                    user_id=user.id, persona_id=persona_id
                )
                db_session.add(db_preferable_persona)

        await db_session.commit()
        return {"message": "Favorite personas added successfully"}
    except SQLAlchemyError as ex:
        await db_session.rollback()
        raise UnprocessableEntityHTTPException(msg=repr(ex)) from ex


# toggle preferable persona
@persona_router.post(
    "/toggle_preferable_persona", status_code=201, response_model=dict[str, str]
)
async def toggle_preferable_persona(
    user: Annotated[User, Depends(get_activated_user)],
    persona_id: Annotated[UUID, Body(embed=True)],
    db_session: AsyncSession = Depends(get_db),
):
    try:
        # check if the persona exists
        db_persona: Persona | None = await Persona.find_by_id(
            db_session=db_session, persona_id=persona_id, user=user
        )
        if not db_persona:
            raise PERSONA_NOT_FOUND

        db_preferable_persona: PreferablePersona | None = (
            await PreferablePersona.find_by_user_id_and_persona_id(
                db_session=db_session, user_id=user.id, persona_id=persona_id
            )
        )
        if db_preferable_persona:
            await db_session.delete(db_preferable_persona)
            await db_session.commit()
            return {"message": "Preferable persona deleted successfully"}
        else:
            db_preferable_persona = PreferablePersona(
                user_id=user.id, persona_id=persona_id
            )
            db_session.add(db_preferable_persona)
            await db_session.commit()
            return {"message": "Preferable persona added successfully"}
    except SQLAlchemyError as ex:
        await db_session.rollback()
        raise UnprocessableEntityHTTPException(msg=repr(ex)) from ex


# get preferable persona of the logged in user
@persona_router.get(
    "/get_preferable_persona",
    response_model=list[PersonaOutWithOutQuotes],
)
async def get_preferable_persona(
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    query = (
        select(Persona)
        .where(Persona.is_active, ~Persona.is_archived)
        .join(PreferablePersona, Persona.id == PreferablePersona.persona_id)
        .join(User, User.id == PreferablePersona.user_id)
        .where(User.id == user.id)
    )

    result = await db_session.execute(query)
    instance = result.scalars().all()
    return instance


@persona_router.get(
    "/search",
    response_model=Paginate[PersonaOut],
)
async def search_persona(
    persona_name: Annotated[str, Query()],
    db_session: AsyncSession = Depends(get_db),
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    persona_type: Annotated[PersonaType, Query()] | None = None,
    user: User = Depends(get_activated_user),
):
    print(persona_name)
    return await Persona.search_persona(
        db_session=db_session,
        persona_name=persona_name,
        persona_type=persona_type,
        offset=offset,
        limit=limit,
        user=user,
    )


@persona_router.get(
    "/get_all_types",
    response_model=list[str],
    dependencies=[Depends(get_activated_user)],
)
async def get_all_persona_types(
    db_session: AsyncSession = Depends(get_db),
):
    # get all the distinct persona types from database
    query = select(Persona.persona_type).distinct()
    result = await db_session.execute(query)
    instance: List[str] = result.scalars().all()
    print(instance)

    return instance


@persona_router.post(
    "/create_persona",
    response_model=PersonaOut,
    status_code=201,
)
async def create_persona_users(
    persona_info: Annotated[PersonaInitialPromptInput, Body()],
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_persona_number_validated_user),
):
    db_persona: Persona | None = await Persona.find_by_full_name(
        db_session=db_session,
        full_name=persona_info.persona_name,
    )
    if db_persona:
        raise PERSONA_NAME_ALREADY_EXISTS

    initial_prompt = create_initial_prompt(persona_info)

    persona = PersonaCreate(
        full_name=persona_info.persona_name,
        persona_type=persona_info.persona_type,
        persona_image=persona_info.persona_image,
        default_color=persona_info.default_color,
        description=persona_info.description,
        long_description=persona_info.description
        + (persona_info.additional_info if persona_info.additional_info else ""),
        initial_prompt=initial_prompt,
        visible=persona_info.visible,
        # TODO: check if the user is premium or not, to accept there input
        has_tool_access=False,
    )

    db_persona = await create_new_persona(
        db_session=db_session, persona=persona, user=user
    )

    return db_persona


@persona_router.get(
    "/discover_personas",
    response_model=Paginate[PersonaOutDiscover],
)
async def discover_personas(
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    return await Persona.get_created_personas(
        db_session=db_session,
        limit=limit,
        offset=offset,
        user=user,
    )


@persona_router.get(
    "/get_my_personas",
    response_model=Paginate[PersonaOutWithVisible],
)
async def get_persona_by_id(
    order_by: Optional[OrderBy] = None,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
    search_query: str = "",
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0,
):
    order_by_mapping = {
        OrderBy.PERSONA_NAME_ASC: Persona.full_name.asc(),
        OrderBy.PERSONA_NAME_DESC: Persona.full_name.desc(),
        OrderBy.CATEGORY_ASC: Persona.persona_type.asc(),
        OrderBy.CATEGORY_DESC: Persona.persona_type.desc(),
    }

    # Get the SQLAlchemy order_by clause based on the user's choice
    order_by_clause = order_by_mapping.get(order_by, Persona.full_name.asc())

    db_personas: List[
        PersonaOutWithVisible
    ] = await Persona.find_by_creator_uuid_pagination(
        db_session=db_session,
        creator_uuid=user.id,
        search_query=search_query,
        limit=limit,
        offset=offset,
        order_by_clause=order_by_clause,
    )

    return db_personas


@persona_router.put(
    "/update_persona",
    response_model=PersonaOut,
)
async def update_persona(
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
    persona: PersonaEditInitialPromptInput = Body(..., embed=True),
    persona_id: UUID = Query(...),
):
    db_persona: Persona | None = await Persona.find_by_id(
        db_session=db_session, persona_id=persona_id, user=user
    )
    #
    if not db_persona:
        raise PERSONA_NOT_FOUND

    if db_persona.creator_uuid != user.id:
        raise UnprocessableEntityHTTPException(
            msg="You are not allowed to edit this persona"
        )

    db_persona = await edit_persona_for_users(
        db_session=db_session, db_persona=db_persona, updated_persona=persona
    )

    return db_persona


@persona_router.delete(
    "/delete_persona",
    response_model=object,
)
async def delete_persona_by_id_soft(
    persona_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
):
    db_persona: Persona | None = await Persona.find_by_id(
        db_session=db_session, persona_id=persona_id, user=user
    )
    if not db_persona:
        raise PERSONA_NOT_FOUND

    if db_persona.creator_uuid != user.id:
        raise UnprocessableEntityHTTPException(
            msg="You are not allowed to delete this persona"
        )

    db_persona.is_active = False
    await db_session.commit()
    return {"message": "Persona deleted successfully"}


@persona_router.delete(
    "/delete_persona_dev",
    response_model=object,
)
async def delete_persona_by_id_hard(
    persona_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(is_admin_user),
):
    db_persona: Persona | None = await Persona.find_by_id(
        db_session=db_session, persona_id=persona_id, user=user
    )
    if not db_persona:
        raise PERSONA_NOT_FOUND

    await db_session.delete(db_persona)
    await db_session.commit()
    return {"message": "Persona deleted from DB successfully"}


@persona_router.get(
    "/get_last_session_id",
    response_model=ChatSessionBaseOutSchema,
)
async def get_user_last_session_with_persona(
    db_session: AsyncSession = Depends(get_db),
    user: User = Depends(get_activated_user),
    persona_id: UUID = Query(...),
):
    from app.routers.api_v1.chat.models import ChatSession

    db_persona: Persona | None = await Persona.find_by_id(
        db_session=db_session, persona_id=persona_id, user=user
    )
    if not db_persona:
        raise PERSONA_NOT_FOUND

    # get the last session id of the user with the persona
    last_chat_session: ChatSessionBaseOutSchema | None = (
        await ChatSession.get_user_last_session_with_persona(
            db_session=db_session, user_id=user.id, persona_id=persona_id
        )
    )

    if not last_chat_session:
        raise NotFoundHTTPException(msg="No chat session found with the persona")

    # transform the chat session to the response model

    return last_chat_session


@persona_router.get(
    "/get_functional_tools_list",
    response_model=list[str],
    dependencies=[Depends(is_admin_user)],
)
async def get_functional_tools_list():
    from app.routers.api_v1.Functional_Tools.constants import functional_tools

    # iterate through the functional tools dict and get the keys
    tools_list: List[str] = [k for k, v in functional_tools.items()]

    return tools_list
