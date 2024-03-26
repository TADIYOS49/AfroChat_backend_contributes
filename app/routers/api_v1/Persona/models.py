import uuid
from datetime import datetime
from typing import List
from app.constants import LLMModels
from app.routers.api_v1.Auth.models import PreferablePersona, User
import re

from sqlalchemy import (
    Integer,
    String,
    false,
    true,
    func,
    select,
    Boolean,
    ForeignKey,
    case,
    and_,
    or_,
)
from sqlalchemy.dialects.postgresql import UUID as sqlalchemy_UUID
from uuid import UUID

from sqlalchemy import ARRAY, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.database.base import Base
from app.routers.api_v1.Persona.schemas import (
    PersonaOut,
    PersonaOutDiscover,
    PersonaOutNoQuotes,
    PersonaType,
    PersonaOutWithVisible,
)
from app.routers.api_v1.Service.utils import paginate_response

"""
Persona (
    persona_id,
    creator_uuid,
    created_at,
    updated_at,
    full_name,
    quotes: [],
    persona_image: image URL,
    default_color: string ,
    Initial_prompt: String,
    persona_type: String,
    is_active: Boolean, default (True)
    is_premium: Boolean, Default False
    
    creator_uuid: foreign key to User table
    visible: Boolean, default (True)
)
"""


# Persona class
class Persona(Base):
    __tablename__ = "persona"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    creator_uuid: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, unique=True
    )
    persona_image: Mapped[str] = mapped_column(String(200), nullable=False)
    default_color: Mapped[str] = mapped_column(String(10), nullable=False)
    initial_prompt: Mapped[str] = mapped_column(String(10000), nullable=False)
    persona_type: Mapped[PersonaType] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=true(), nullable=False
    )
    is_premium: Mapped[bool] = mapped_column(server_default=false(), nullable=False)
    description: Mapped[str] = mapped_column(String(3000), nullable=False)
    long_description: Mapped[str] = mapped_column(String(3000), nullable=False)
    is_archived: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=False
    )

    visible: Mapped[bool] = mapped_column(
        Boolean, server_default=true(), nullable=False
    )

    quotes: Mapped[List["Quotes"]] = relationship(
        "Quotes", back_populates="persona", cascade="all,delete"
    )

    creator: Mapped[User] = relationship("User", foreign_keys="Persona.creator_uuid")

    functional_tools: Mapped[List[str]] = mapped_column(
        ARRAY(String(1000)),
        server_default=text("'{}'::character varying[]"),
        nullable=False,
    )
    llm_model: Mapped[str] = mapped_column(
        String(100),
        server_default=LLMModels.MISTRAL.value,
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    total_messages: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )

    @classmethod
    async def get_all_personas_by_preference(
        cls,
        db_session: AsyncSession,
        user: User,
        limit: int = 10,
        offset: int = 0,
    ):
        subquery = (
            select(
                func.max(
                    case(
                        (
                            (
                                PreferablePersona.user_id == user.id,
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
            .options(selectinload(Persona.quotes))
            .where(Persona.is_active, ~Persona.is_archived, Persona.visible)
        )

        return await paginate_response(
            statement=query,
            db_session=db_session,
            model=PersonaOutNoQuotes,
            offset=offset,
            limit=limit,
            sorting_attribute=cls.created_at.asc(),
            transformer=lambda rows: [
                PersonaWithPreference(row.Persona, row.is_preferable_persona).persona
                for row in rows
            ],
        )

    @classmethod
    async def get_all_personas_pagination(
        cls,
        db_session: AsyncSession,
        order_by_clause,
        limit: int = 20,
        offset: int = 0,
        is_archived: bool = False,
        user: User = None,
    ):
        if is_archived:
            stmt = (
                select(cls)
                .options(selectinload(cls.quotes))
                .where(
                    and_(
                        ~cls.is_active,
                        or_(cls.visible, cls.creator_uuid == user.id),
                    )
                )
            )
        else:
            stmt = (
                select(cls)
                .options(selectinload(cls.quotes))
                .where(
                    and_(cls.is_active, or_(cls.visible, cls.creator_uuid == user.id))
                )
            )

        return await paginate_response(
            statement=stmt,
            db_session=db_session,
            model=PersonaOut,
            offset=offset,
            limit=limit,
            sorting_attribute=order_by_clause,
            to_orm=True,
        )

    @classmethod
    async def get_all(cls, db_session: AsyncSession):
        """
        Retrieve all active Persona instances along with their associated quotes.

        This method retrieves all active Persona instances from the database and joins them with their associated quotes. It returns a list of Persona objects with quotes preloaded.

        :param db_session: An AsyncSession object representing a database session.
        :type db_session: AsyncSession

        :return: A list of Persona objects with associated quotes.
        :rtype: list[Persona]
        """
        stmt = (
            select(cls)
            .options(selectinload(cls.quotes))
            .where(and_(cls.is_active, ~cls.is_archived, cls.visible))
        )

        result = await db_session.execute(stmt)

        instance: List[Persona] = list(result.scalars().all())

        return instance

    @classmethod
    async def find_by_id(
        cls, db_session: AsyncSession, persona_id: uuid.UUID, user: User
    ):
        """
        :param db_session:
        :param persona_id:
        :param user:
        :return:
        """
        stmt = (
            select(cls)
            .options(selectinload(cls.quotes))
            .where(
                and_(
                    cls.id == persona_id,
                    cls.is_active,
                    ~cls.is_archived,
                    or_(cls.visible, cls.creator_uuid == user.id),
                )
            )
            .limit(1)
        )
        result = await db_session.execute(stmt)

        # return the first persona with the same id
        instance: Persona | None = result.scalars().first()
        return instance

    @classmethod
    async def find_multiple_by_id(
        cls, db_session: AsyncSession, persona_ids: List[uuid.UUID]
    ):
        """
        :param db_session:
        :param persona_ids:
        :return:
        """
        stmt = (
            select(cls)
            .filter(cls.id.in_(persona_ids))
            .options(selectinload(cls.quotes))
        )
        result = await db_session.execute(stmt)
        instances: List[Persona] = result.scalars().all()
        return instances

    @classmethod
    async def find_by_creator_uuid(cls, db_session: AsyncSession, creator_uuid: UUID):
        """
        :param db_session:
        :param creator_uuid:
        :return:
        """
        stmt = (
            select(cls)
            .options(selectinload(cls.quotes))
            .where(and_(cls.creator_uuid == creator_uuid, cls.is_active))
        )
        result = await db_session.execute(stmt)

        # return all personas created by the user
        instance: List[Persona] = list(result.scalars().all())
        return instance

    @classmethod
    def initial_prompt_parser(cls, prompt_string):
        # Define regular expressions to match the desired information
        age_pattern = r"Persona Age: (\d+)"
        occupation_pattern = r"Persona Occupation: (\w+)"
        additional_info_pattern = r"Persona Additional Info:(.+)"

        # Extract information using regular expressions
        age_match = re.search(age_pattern, prompt_string)
        occupation_match = re.search(occupation_pattern, prompt_string)
        additional_info_match = re.search(additional_info_pattern, prompt_string)

        # Initialize variables to store extracted information
        persona_age = None
        persona_occupation = None
        persona_additional_info = None

        # Extract information from the matched groups if found
        if age_match:
            persona_age = int(age_match.group(1))
        if occupation_match:
            persona_occupation = occupation_match.group(1).strip()
        if additional_info_match:
            persona_additional_info = additional_info_match.group(1).strip()

        # Return the extracted information
        return persona_age, persona_occupation, persona_additional_info

    @classmethod
    async def find_by_creator_uuid_pagination(
        cls,
        db_session: AsyncSession,
        creator_uuid: UUID,
        search_query: str,
        limit: int = 10,
        offset: int = 0,
        order_by_clause=None,
    ):
        """
        :param db_session:
        :param creator_uuid:
        :param limit:
        :param offset:
        :return:
        """
        stmt = (
            select(cls)
            .options(selectinload(cls.quotes))
            .where(
                and_(
                    cls.creator_uuid == creator_uuid,
                    cls.is_active,
                    ~cls.is_archived,
                    cls.full_name.ilike(f"%{search_query}%"),
                )
            )
        )

        def transform(personas: [Persona]):
            return [
                PersonaOutWithVisible(
                    id=persona.id,
                    full_name=persona.full_name,
                    persona_type=persona.persona_type,
                    persona_image=persona.persona_image,
                    default_color=persona.default_color,
                    description=persona.description,
                    long_description=persona.long_description,
                    is_premium=persona.is_premium,
                    creator_uuid=persona.creator_uuid,
                    created_at=persona.created_at,
                    quotes=persona.quotes,
                    visible=persona.visible,
                    **dict(
                        zip(
                            ["age", "occupation", "additional_info"],
                            Persona.initial_prompt_parser(persona.initial_prompt),
                        )
                    ),
                )
                for persona in personas
            ]

        return await paginate_response(
            statement=stmt,
            db_session=db_session,
            model=PersonaOutWithVisible,
            transformer=transform,
            offset=offset,
            limit=limit,
            sorting_attribute=order_by_clause,
            to_orm=True,
        )

    # FIXME THIS IS SO WRONG
    @classmethod
    async def find_by_persona_type2(
        cls,
        db_session: AsyncSession,
        persona_type: PersonaType,
        user: User,
        limit: int = 10,
        offset: int = 0,
    ):
        """
        :param db_session:
        :param persona_type:
        :param user:
        :param limit:
        :param offset:
        :return: persona
        """
        subquery = (
            select(
                func.max(
                    case(
                        (
                            (
                                PreferablePersona.user_id == user.id,
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
            .options(selectinload(Persona.quotes))
            .where(
                and_(
                    Persona.is_active,
                    Persona.visible,
                    ~Persona.is_archived,
                    Persona.persona_type == persona_type.value,
                    or_(Persona.visible, Persona.creator_uuid == user.id),
                )
            )
            .limit(limit)
            .offset(offset)
        )
        results = await db_session.execute(query)

        list_of_persona: list[PersonaWithPreference] = [
            PersonaWithPreference(row.Persona, row.is_preferable_persona).persona
            for row in results.fetchall()
        ]

        return list_of_persona

    @classmethod
    async def find_by_persona_type(
        cls,
        db_session: AsyncSession,
        persona_type: PersonaType,
        user: User,
        limit: int = 10,
        offset: int = 0,
    ):
        """
        :param db_session:
        :param persona_type:
        :param user:
        :param limit:
        :param offset:
        :return: persona
        """
        subquery = (
            select(
                func.max(
                    case(
                        (
                            (
                                PreferablePersona.user_id == user.id,
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
            .options(selectinload(Persona.quotes))
            .where(
                and_(
                    Persona.is_active,
                    Persona.visible,
                    ~Persona.is_archived,
                    Persona.persona_type == persona_type.value,
                    or_(Persona.visible, Persona.creator_uuid == user.id),
                )
            )
        )

        return await paginate_response(
            statement=query,
            db_session=db_session,
            model=PersonaOutNoQuotes,
            offset=offset,
            limit=limit,
            sorting_attribute=cls.created_at.asc(),
            transformer=lambda rows: [
                PersonaWithPreference(row.Persona, row.is_preferable_persona).persona
                for row in rows
            ],
        )

    @classmethod
    async def find_by_full_name(
        cls,
        db_session: AsyncSession,
        full_name: str,
    ):
        """
        :param db_session:
        :param full_name:
        :return:
        """
        stmt = select(cls).where(
            cls.full_name == full_name,
        )
        result = await db_session.execute(stmt)
        # return the first persona with the same full name
        instance: Persona | None = result.scalars().first()
        return instance

    @classmethod
    async def search_persona(
        cls,
        db_session: AsyncSession,
        persona_name: str,
        persona_type: PersonaType | None,
        offset: int,
        limit: int,
        user: User,
        is_archived: bool = False,
        order_by_clause=None,
    ):
        """
        :param db_session:
        :param persona_name:
        :param persona_type:
        :param offset:
        :param limit:
        :param user:
        :param is_archived:
        :param order_by_clause:
        """
        query = (
            select(cls)
            .options(selectinload(cls.quotes))
            .where(
                and_(
                    cls.is_active == (not is_archived),
                    cls.visible,
                    cls.is_archived == is_archived,
                    cls.full_name.ilike(f"%{persona_name}%"),
                    or_(cls.visible, cls.creator_uuid == user.id),
                )
            )
        )
        if persona_type:
            query = query.where(cls.persona_type == persona_type.value)

        if order_by_clause is None:
            order_by_clause = cls.created_at.asc()

        return await paginate_response(
            statement=query,
            db_session=db_session,
            model=PersonaOut,
            offset=offset,
            limit=limit,
            sorting_attribute=order_by_clause,
            to_orm=True,
        )

    @classmethod
    async def get_created_personas(
        cls,
        db_session: AsyncSession,
        offset: int,
        limit: int,
        user: User,
    ):
        query = (
            select(cls)
            .options(selectinload(cls.creator))
            .where(cls.visible, cls.is_active, ~cls.is_archived)
        )

        def transform(personas: [Persona]):
            return [
                PersonaOutDiscover(
                    id=persona.id,
                    full_name=persona.full_name,
                    persona_type=persona.persona_type,
                    persona_image=persona.persona_image,
                    default_color=persona.default_color,
                    description=persona.description,
                    long_description=persona.long_description,
                    is_premium=persona.is_premium,
                    creator_uuid=persona.creator_uuid,
                    created_at=persona.created_at,
                    created_by=persona.creator.username,
                )
                for persona in personas
            ]

        return await paginate_response(
            statement=query,
            db_session=db_session,
            model=PersonaOutDiscover,
            transformer=transform,
            offset=offset,
            limit=limit,
            sorting_attribute=cls.score.desc(),
            to_orm=True,
        )


class PersonaWithPreference:
    def __init__(self, persona, is_preferable_persona):
        self.persona = persona
        self.persona.is_preferable_persona = is_preferable_persona


class Quotes(Base):
    __tablename__ = "quotes"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    quote: Mapped[str] = mapped_column(String(10000), nullable=False)
    persona_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("persona.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    persona: Mapped["Persona"] = relationship("Persona", back_populates="quotes")

    def __init__(self, persona_id: UUID, quote: str):
        super().__init__()
        self.quote = quote
        self.persona_id = persona_id
