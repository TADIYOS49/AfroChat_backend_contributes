import uuid
from sqlalchemy import true, Boolean
from sqlalchemy import String, select
from sqlalchemy.dialects.postgresql import UUID as sqlalchemy_UUID
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Version(Base):
    __tablename__ = "version"

    version_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    version: Mapped[String] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=true(), nullable=False
    )

    @classmethod
    async def check_version(cls, db_session: AsyncSession, version: str):
        statement = select(cls).filter(cls.version == version)
        result = await db_session.execute(statement)
        instance = result.scalar_one_or_none()

        if not instance:
            return False

        return instance.is_active

    @classmethod
    async def find_by_version_name(cls, db_session: AsyncSession, version: str):
        statement = select(cls).filter(cls.version == version)
        result = await db_session.execute(statement)
        instance: Version | None = result.scalars().first()

        return instance
