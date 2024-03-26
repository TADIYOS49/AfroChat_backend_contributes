import uuid
from datetime import datetime
from enum import Enum
from typing import List


from app.routers.api_v1.Service.utils import paginate_response

from sqlalchemy import BIGINT, String, false, func, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as sqlalchemy_UUID
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.database.base import Base
from app.utils.logger import FastApiLogger


"""
A Fan-in user model.

telegram_user:
    user_id: UUID, ForeignKey(user.id), Indexed, PK
    telegram_id: String, Len(100), Unique, PK
    created_at: Datetime
    
user_phone_number:
    user_id: UUID, ForeignKey(user.id), Indexed, PK
    phone_number: String, Len(15), Unique, PK
    created_at: Datetime, Default Now
    updated_at: Datetime
    is_activated: Boolean, Default False
    
user_email:
    user_id: UUID, ForeignKey(user.id), Indexed, PK
    email: String, Len(50), Unique, PK
    created_at: Datetime, Default Now
    updated_at: Datetime
    is_activated: Boolean, Default False

user_profile_picture:
    user_id: UUID, ForeignKey(user.id), Unique, PK
    profile_picture: String, Len(200)
    created_at: Datetime, Default Now
    updated_at: Datetime   
    
user_password:
    user_id: UUID, ForeignKey(user.id), Unique, PK
    hashed_password: String, Len(200)
    created_at: Datetime, Default Now
    updated_at: Datetime

# Fan-in  
user:
    id: UUID, PK, Unique
    # if null, generate a random 8 - character string
    username: String, Len(50), Unique, Indexed
    role: Enum, Default USER
    created_at: Datetime, Default Now
    updated_at: Datetime, Default Now
    is_archived: Boolean, Default False
    is_activated: Boolean, Default False
    is_premium: Boolean, Default False
"""


class Role(Enum):
    USER = 1
    ADMIN = 2
    SUPER_ADMIN = 3


class SignUpPlatform(Enum):
    TELEGRAM = 1
    MOBILE = 2


class OtpReason(Enum):
    ACTIVATE = 1
    RESET_PASSWORD = 2


class AskTelegram(Base):
    __tablename__ = "ask_telegram"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
        primary_key=True,
        index=True,
    )

    question: Mapped[str] = mapped_column(String(100000), nullable=False)
    answer: Mapped[str] = mapped_column(String(100000), nullable=False)
    token_usage: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="ask_telegram")

    # if it's 99 then it means it not from a group
    group_id: Mapped[int] = mapped_column(
        BIGINT,
        server_default="99",
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    @classmethod
    async def find_by_user_id(cls, db_session: AsyncSession, user_id: UUID):
        """
        :param db_session:
        :param user_id:
        :return:
        """
        return list(
            (await db_session.execute(select(cls).filter(cls.user_id == user_id)))
            .scalars()
            .all()
        )

    @classmethod
    async def add_ask_telegram(
        cls,
        db_session: AsyncSession,
        user_id: UUID,
        question: str,
        answer: str,
        token_usage: int,
        group_id: int,
    ):
        """
        :param db_session:
        :param user_id:
        :param question:
        :param answer:
        :param token_usage:
        :return:
        """
        ask_telegram = AskTelegram(
            user_id=user_id,
            question=question,
            answer=answer,
            token_usage=token_usage,
            group_id=group_id,
        )
        try:
            db_session.add(ask_telegram)
            await db_session.commit()
            return ask_telegram
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise Exception(str(e))


class UserTelegram(Base):
    __tablename__ = "user_telegram"

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
        primary_key=True,
        index=True,
    )
    telegram_id: Mapped[str] = mapped_column(
        String(100), unique=True, primary_key=True, index=True
    )
    full_name: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="telegram_user")

    telegram_group_messages: Mapped[list["TelegramGroupMessage"]] = relationship(
        "TelegramGroupMessage",
        back_populates="telegram_user",
        primaryjoin="foreign(cast(UserTelegram.telegram_id, BigInteger)) == TelegramGroupMessage.telegram_id",
    )

    @classmethod
    async def find_no_join(cls, db_session: AsyncSession, telegram_id: str):
        """
        :param db_session:
        :param telegram_id:
        :return:
        this does not join the user table
        """
        return (
            await db_session.execute(
                select(cls).filter(
                    cls.telegram_id == telegram_id,
                )
            )
        ).scalar_one_or_none()

    @classmethod
    async def find(cls, db_session: AsyncSession, telegram_id: str):
        """
        :param db_session:
        :param telegram_id:
        :return:
        """
        return (
            await db_session.execute(
                select(cls)
                .filter(cls.telegram_id == telegram_id)
                .options(selectinload(cls.user))
            )
        ).scalar_one_or_none()

    @classmethod
    async def find_by_user_id(cls, db_session: AsyncSession, user_id: UUID):
        """
        :param db_session:
        :param user_id:
        :return:
        """
        return (
            await db_session.execute(select(cls).where(cls.user_id == user_id))
        ).scalar_one_or_none()


class UserPhoneNumber(Base):
    __tablename__ = "user_phone_number"

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
        primary_key=True,
        index=True,
    )
    phone_number: Mapped[str] = mapped_column(
        String(15), unique=True, primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    is_activated: Mapped[bool] = mapped_column(server_default=false(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="phone_numbers")

    @classmethod
    async def find(cls, db_session: AsyncSession, phone_number: str):
        """
        :param db_session:
        :param phone_number:
        :return:
        """
        return (
            await db_session.execute(
                select(cls).filter(cls.phone_number == phone_number)
            )
        ).scalar_one_or_none()

    @classmethod
    async def find_by_user_id(cls, db_session: AsyncSession, user_id: UUID):
        """
        :param db_session:
        :param user_id:
        :return:
        """
        return (
            await db_session.execute(select(cls).filter(cls.user_id == user_id))
        ).scalar_one_or_none()


class UserEmail(Base):
    __tablename__ = "user_email"

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
        primary_key=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(50), unique=True, primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    is_activated: Mapped[bool] = mapped_column(server_default=false(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="emails")

    @classmethod
    async def find(cls, db_session: AsyncSession, email: str):
        """
        :param db_session:
        :param email:
        :return:
        """
        return (
            await db_session.execute(select(cls).filter(cls.email == email))
        ).scalar_one_or_none()

    @classmethod
    async def find_by_user_id(cls, db_session: AsyncSession, user_id: UUID):
        """
        :param db_session:
        :param user_id:
        :return:
        """
        return (
            await db_session.execute(select(cls).where(cls.user_id == user_id))
        ).scalar_one_or_none()


class UserProfilePicture(Base):
    __tablename__ = "user_profile_picture"

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
        primary_key=True,
        index=True,
    )
    profile_picture: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    @classmethod
    async def find_by_user_id(cls, db_session: AsyncSession, user_id: UUID):
        """
        :param db_session:
        :param user_id:
        :return:
        """
        return (
            await db_session.execute(select(cls).filter(cls.user_id == user_id))
        ).scalar_one_or_none()


class UserPassword(Base):
    __tablename__ = "user_password"

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        ForeignKey("user.id"),
        primary_key=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    # if null, generate a random 8 - character string
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    role: Mapped[int] = mapped_column(default=Role.USER.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    is_archived: Mapped[bool] = mapped_column(server_default=false(), nullable=False)
    is_activated: Mapped[bool] = mapped_column(server_default=false(), nullable=False)
    is_premium: Mapped[bool] = mapped_column(server_default=false(), nullable=False)
    is_developer: Mapped[bool] = mapped_column(server_default=false(), nullable=False)
    signup_platform: Mapped[int] = mapped_column(
        default=SignUpPlatform.MOBILE.value, nullable=False
    )

    telegram_user: Mapped[List["UserTelegram"]] = relationship(
        "UserTelegram", back_populates="user", cascade="all,delete"
    )

    user_info: Mapped["UserInfo"] = relationship(
        "UserInfo", back_populates="user", foreign_keys="UserInfo.user_id"
    )

    phone_numbers: Mapped[List["UserPhoneNumber"]] = relationship(
        "UserPhoneNumber", back_populates="user", cascade="all,delete"
    )
    emails: Mapped[List["UserEmail"]] = relationship(
        "UserEmail", back_populates="user", cascade="all,delete"
    )
    profile_picture: Mapped["UserProfilePicture"] = relationship(
        "UserProfilePicture", cascade="all,delete"
    )
    password: Mapped["UserPassword"] = relationship(
        "UserPassword", cascade="all,delete"
    )
    ask_telegram: Mapped[List["AskTelegram"]] = relationship(
        "AskTelegram", back_populates="user", cascade="all,delete"
    )
    phone_otp: Mapped[List["Phone_Otp"]] = relationship(
        "Phone_Otp", back_populates="user", cascade="all,delete"
    )
    email_otp: Mapped[List["Email_Otp"]] = relationship(
        "Email_Otp", back_populates="user", cascade="all,delete"
    )

    @classmethod
    async def get_all_pagination(
        cls,
        db_session: AsyncSession,
        order_by_clause,
        search: str,
        limit: int = 20,
        offset: int = 0,
    ):
        from app.routers.api_v1.Auth.schemas import UserOutAdmin

        orders = [
            User.username.asc(),
            User.username.desc(),
            User.role.asc(),
            User.role.desc(),
            User.created_at.asc(),
            User.created_at.desc(),
        ]

        stmt = (
            select(cls)
            .options(
                selectinload(cls.emails),
                selectinload(cls.phone_numbers),
                selectinload(cls.profile_picture),
                selectinload(cls.telegram_user),
                selectinload(cls.password),
                selectinload(cls.user_info),
            )
            .where(
                cls.is_activated,
                cls.username.ilike(f"%{search}%"),
            )
        )

        def transform(users: [User]):
            return [UserOutAdmin.from_orm(user) for user in users]

        return await paginate_response(
            statement=stmt,
            db_session=db_session,
            model=UserOutAdmin,
            transformer=transform,
            offset=offset,
            limit=limit,
            sorting_attribute=order_by_clause,
            to_orm=True,
        )

    @classmethod
    async def find(cls, db_session: AsyncSession, user_id: UUID):
        """
        :param db_session: AsyncSession
        :param user_id: UUID
        :return: User | None
        """
        stmt = (
            select(cls)
            .filter(cls.id == user_id)
            .options(
                selectinload(cls.emails),
                selectinload(cls.phone_numbers),
                selectinload(cls.profile_picture),
                selectinload(cls.telegram_user),
                selectinload(cls.password),
                selectinload(cls.user_info),
            )
        )
        result = await db_session.execute(stmt)
        instance: User | None = result.scalar_one_or_none()
        return instance

    @classmethod
    async def find_multiple(cls, db_session: AsyncSession, user_ids: List[UUID]):
        """
        :param db_session: AsyncSession
        :param user_id: UUID
        :return: User | None
        """
        stmt = (
            select(cls)
            .filter(cls.id.in_(user_ids))
            .options(
                selectinload(cls.emails),
                selectinload(cls.phone_numbers),
                selectinload(cls.profile_picture),
                selectinload(cls.telegram_user),
                selectinload(cls.password),
                selectinload(cls.user_info),
            )
        )
        result = await db_session.execute(stmt)
        instances: List[User] = result.scalars().all()
        return instances

    @classmethod
    async def find_by_username(cls, db_session: AsyncSession, username: str):
        """
        :param db_session: AsyncSession
        :param username: str of username
        :return: User | None
        """
        stmt = (
            select(cls)
            .filter(cls.username == username)
            .options(
                selectinload(cls.emails),
                selectinload(cls.phone_numbers),
                selectinload(cls.profile_picture),
                selectinload(cls.telegram_user),
                selectinload(cls.password),
                selectinload(cls.user_info),
            )
        )

        result = await db_session.execute(stmt)
        instance: User | None = result.scalar_one_or_none()
        return instance

    @classmethod
    async def find_by_email(cls, db_session: AsyncSession, email: str):
        """
        :param db_session: AsyncSession
        :param email: str of email
        :return: User | None
        """
        stmt = (
            select(cls)
            .join(UserEmail, UserEmail.user_id == User.id)
            .filter(UserEmail.email == email)
            .options(
                selectinload(cls.emails),
                selectinload(cls.phone_numbers),
                selectinload(cls.profile_picture),
                selectinload(cls.telegram_user),
                selectinload(cls.password),
                selectinload(cls.user_info),
            )
        )

        result = await db_session.execute(stmt)
        instance: User | None = result.scalars().first()
        return instance

    @classmethod
    async def find_by_phone_number(cls, db_session: AsyncSession, phone_number: str):
        """
        :param db_session:
        :param phone_number: str of phone number
        :return: User | None
        """
        stmt = (
            select(cls)
            .join(UserPhoneNumber, UserPhoneNumber.user_id == cls.id)
            .filter(UserPhoneNumber.phone_number == phone_number)
            .options(
                selectinload(cls.emails),
                selectinload(cls.phone_numbers),
                selectinload(cls.profile_picture),
                selectinload(cls.telegram_user),
                selectinload(cls.password),
                selectinload(cls.user_info),
            )
        )

        result = await db_session.execute(stmt)
        instance: User | None = result.scalars().first()
        return instance

    @classmethod
    async def find_by_telegram_id(cls, db_session: AsyncSession, telegram_id: str):
        """
        :param db_session: AsyncSession
        :param telegram_id: str of telegram id
        :return: User | None
        """
        stmt = (
            select(cls)
            .join(UserTelegram, UserTelegram.user_id == cls.id)
            .filter(UserTelegram.telegram_id == telegram_id)
            .options(
                selectinload(cls.emails),
                selectinload(cls.phone_numbers),
                selectinload(cls.profile_picture),
                selectinload(cls.telegram_user),
                selectinload(cls.user_info),
            )
        )

        result = await db_session.execute(stmt)
        instance: User | None = result.scalar_one_or_none()
        return instance

    @classmethod
    async def get_all(cls, db_session: AsyncSession):
        stmt = select(cls).options(
            selectinload(cls.emails),
            selectinload(cls.phone_numbers),
            selectinload(cls.profile_picture),
            selectinload(cls.telegram_user),
            selectinload(cls.user_info),
        )

        result = await db_session.execute(stmt)
        instance: List[User] = list(result.scalars().all())

        return instance


class Email_Otp(Base):
    __tablename__ = "email_otp"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("user.id"), index=True
    )

    user: Mapped["User"] = relationship("User")

    is_used: Mapped[bool] = mapped_column(server_default=false(), nullable=False)

    email_instance: Mapped["UserEmail"] = relationship("UserEmail")

    email: Mapped[UUID] = mapped_column(
        String(50),
        ForeignKey("user_email.email"),
        index=True,
    )
    otp: Mapped[str] = mapped_column(String(50))
    reason: Mapped[int] = mapped_column(
        default=OtpReason.ACTIVATE.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    @classmethod
    async def find(cls, db_session: AsyncSession, email: str):
        """
        :param db_session: AsyncSession
        :param email: str of email
        :return: Email_Otp | None
        """
        stmt = select(cls).filter(cls.email == email)

        result = await db_session.execute(stmt)
        instance: Email_Otp | None = result.scalar_one_or_none()
        return instance

    @classmethod
    async def find_otp_by_active_user(
        cls,
        db_session: AsyncSession,
        user_id: UUID,
        otp_reason: int,
    ):
        """
        :param db_session:
        :param user_id:
        :param otp_purpose:
        :return:
        """
        stmt = (
            select(cls)
            .join(User, User.id == cls.user_id)
            .options(selectinload(cls.user))
            .where(
                User.id == user_id,
                cls.reason == otp_reason,
                User.is_activated,
                ~cls.is_used,
            )
        )
        result = await db_session.execute(stmt)
        instance: Email_Otp | None = result.scalars().first()
        return instance


class Phone_Otp(Base):
    __tablename__ = "phone_otp"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("user.id"), index=True
    )

    is_used: Mapped[bool] = mapped_column(server_default=false(), nullable=False)

    user: Mapped["User"] = relationship("User")

    phone_number_instance: Mapped["UserPhoneNumber"] = relationship("UserPhoneNumber")

    phone_number: Mapped[str] = mapped_column(
        String(15),
        ForeignKey("user_phone_number.phone_number"),
        index=True,
    )
    otp: Mapped[str] = mapped_column(String(50))
    reason: Mapped[int] = mapped_column(
        default=OtpReason.ACTIVATE.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    @classmethod
    async def find(cls, db_session: AsyncSession, phone_number: str):
        """
        :param db_session: AsyncSession
        :param phone_number: str of phone number
        :return: Phone_Otp | None
        """
        stmt = select(cls).filter(cls.phone_number == phone_number)

        result = await db_session.execute(stmt)
        instance: Phone_Otp | None = result.scalar_one_or_none()
        return instance

    @classmethod
    async def find_otp_by_active_user(
        cls,
        db_session: AsyncSession,
        user_id: UUID,
        otp_reason: int,
    ):
        """
        :param db_session:
        :param user_id:
        :param otp_purpose:
        :return:
        """
        stmt = (
            select(cls)
            .join(User, User.id == cls.user_id)
            .options(selectinload(cls.user))
            .where(
                User.id == user_id,
                cls.reason == otp_reason,
                User.is_activated,
                ~cls.is_used,
            )
        )
        FastApiLogger.debug(otp_reason)
        result = await db_session.execute(stmt)
        instance: Phone_Otp | None = result.scalars().first()
        FastApiLogger.debug(instance)
        return instance


class UserInfo(Base):
    __tablename__ = "user_info"
    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("user.id"), index=True
    )

    creator_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("user.id"), index=True
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="user_info", foreign_keys="UserInfo.user_id"
    )

    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class UserGeneratedImages(Base):
    __tablename__ = "user_generated_images"
    id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("user.id"), index=True
    )
    prompt: Mapped[str] = mapped_column(String(10000), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), index=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        BIGINT, server_default="-1001887387943", nullable=False
    )
    group_name: Mapped[str] = mapped_column(
        String(1000), server_default="AfroChat Discussion", nullable=False
    )
    message_id: Mapped[str] = mapped_column(
        String(100),
        server_default="-99",
        nullable=False,
        index=True,
    )  # we don't know the message_id for the previous messages

    @classmethod
    async def total_generated_image(
        cls,
        db_session: AsyncSession,
        user_id: UUID,
        date: datetime,
    ):
        """
        :param db_session:
        :param user_id:
        :param date:
        :return:
        """
        stmt = select(func.count(cls.id)).where(
            cls.user_id == user_id, func.date(cls.created_at) == date.date()
        )
        result = await db_session.execute(stmt)
        instance: int | None = result.scalar()
        return instance

    @classmethod
    async def get_by_message_id(cls, db_session: AsyncSession, message_id: str):
        query = select(cls).where(cls.message_id == message_id)
        result = await db_session.execute(query)
        instance: UserGeneratedImages | None = result.scalar_one_or_none()
        return instance

    @classmethod
    async def add_new_generated_image(
        cls,
        db_session: AsyncSession,
        user_id: UUID,
        prompt: str,
        image_url: str,
        group_id: int,
        group_name: str,
        message_id: str,
    ):
        """
        :param db_session:
        :param user_id:
        :param image_url:
        :return:
        """
        new_generated_image = UserGeneratedImages(
            user_id=user_id,
            image_url=image_url,
            prompt=prompt,
            group_id=group_id,
            group_name=group_name,
            message_id=message_id,
        )
        try:
            db_session.add(new_generated_image)
            await db_session.commit()
            return new_generated_image
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise Exception(str(e))


# create preferable persona that is going to store the user_id and persona_id
class PreferablePersona(Base):
    __tablename__ = "preferable_persona"

    user_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True
    )
    persona_id: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID(as_uuid=True), primary_key=True
    )

    @classmethod
    async def find_by_user_id_and_persona_id(
        cls, db_session: AsyncSession, user_id: UUID, persona_id: UUID
    ):
        stmt = select(cls).where(
            (cls.user_id == user_id) & (cls.persona_id == persona_id)
        )
        result = await db_session.execute(stmt)
        instance: PreferablePersona | None = result.scalars().first()
        return instance
