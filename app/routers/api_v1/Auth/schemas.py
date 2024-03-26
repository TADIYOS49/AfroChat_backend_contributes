import re
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from app.routers.api_v1.Auth.models import Role, SignUpPlatform, User

from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr | None = None
    phone_number: str | None = None
    telegram_id: str | None = None

    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        # trim the phone number
        if not v:
            return None
        v = v.strip()
        # Ethiopia's country code is +251
        pattern = re.compile(r"^\+251\d{9}$")
        if v and not pattern.match(v):
            raise ValueError(
                "Invalid phone number. It must be an Ethiopian number starting with +251"
            )
        return v

    @field_validator("email")
    def validate_email(cls, v):
        # trim the email, reject empty string
        if v and not v.strip():
            raise ValueError("Email cannot be empty")
        return v.strip() if v else None

    @field_validator("username")
    def validate_username(cls, v):
        # trim the username, reject empty string
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()


class UserCreate(UserBase):
    password: str = Field(...)

    @field_validator("password")
    def validate_password(cls, v):
        # trim the password, reject empty string
        if not v.strip():
            raise ValueError("Password cannot be empty")
        return v.strip()


class UpdateUserProfile(BaseModel):
    username: str | None = Field(None, max_length=50)
    profile_picture: HttpUrl | None = None
    old_password: str | None = None
    new_password: str | None = None

    @field_validator("username")
    def validate_username(cls, v):
        # trim the username, reject empty string
        if v and not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip() if v else None

    @field_validator("old_password")
    def validate_old_password(cls, v):
        # trim the password, reject empty string
        if v and not v.strip():
            raise ValueError("Password cannot be empty")
        return v.strip() if v else None

    @field_validator("new_password")
    def validate_new_password(cls, v):
        # trim the password, reject empty string
        if v and not v.strip():
            raise ValueError("Password cannot be empty")
        return v.strip() if v else None

    @field_validator("profile_picture")
    def validate_profile_picture(cls, v):
        # trim the profile_picture, reject empty string
        if isinstance(v, str) and not v.strip():
            raise ValueError("Profile picture cannot be empty")
        return v.strip() if isinstance(v, str) else v


class UserOut(UserBase):
    id: UUID
    profile_picture: HttpUrl | str | None = (
        "https://sm.ign.com/ign_nordic/cover/a/avatar-gen/avatar-generations_prsz.jpg"
    )
    created_at: datetime
    is_activated: bool
    role: str
    telegram_id: Optional[str] = None
    signup_platform: str

    has_password: bool = False

    @classmethod
    def from_orm(cls, user: User):
        return cls(
            id=user.id,
            username=user.username,
            email=user.emails[0].email if user.emails else None,
            phone_number=user.phone_numbers[0].phone_number
            if user.phone_numbers
            else None,
            profile_picture=(
                user.profile_picture.profile_picture
                if user.profile_picture
                else "https://sm.ign.com/ign_nordic/cover/a/avatar-gen/avatar-generations_prsz.jpg"
            ),
            telegram_id=user.telegram_user[0].telegram_id
            if user.telegram_user
            else None,
            created_at=user.created_at,
            is_activated=user.is_activated,
            role=Role(user.role).name,
            signup_platform=SignUpPlatform(user.signup_platform).name,
        )


class TelegramUserOut(BaseModel):
    access_token: str | None = None
    user: UserOut | None = None


class OtpVerify(BaseModel):
    otp: str = Field(..., max_length=10)
    user_id: UUID

    @field_validator("otp")
    def validate_otp(cls, v):
        # trim the password, reject empty string
        if not v.strip():
            raise ValueError("OTP cannot be empty")
        return v.strip()


class OtpVerifyWithPreferablePersona(BaseModel):
    otp: str
    user_id: UUID
    preferable_personas: List[UUID]

    @field_validator("otp")
    def validate_otp(cls, v):
        # trim the password, reject empty string
        if not v.strip():
            raise ValueError("OTP cannot be empty")
        return v.strip()


class TelegramUserAuth(BaseModel):
    id: int | str
    is_bot: bool = False
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    allows_write_to_pm: bool = True

    @field_validator("username")
    def validate_username(cls, v):
        # trim the password, reject empty string
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()


# always validate each request from telegram
class TelegramAuthenticationSchema(BaseModel):
    hash_str: str
    initData: str
    telegram_user: TelegramUserAuth


class UserOutAdmin(BaseModel):
    id: UUID
    first_name: str | None
    last_name: str | None
    username: str
    email: EmailStr | None
    phone_number: str | None
    role: str
    profile_picture: HttpUrl | None
    creator_id: UUID | None
    created_at: datetime
    updated_at: datetime
    is_activated: bool
    is_archived: bool
    signup_platform: str

    @classmethod
    def from_orm(cls, user: User):
        from app.routers.api_v1.Auth.models import Role

        return cls(
            id=user.id,
            first_name=user.user_info.first_name if user.user_info else None,
            last_name=user.user_info.last_name if user.user_info else None,
            username=user.username,
            email=user.emails[0].email if user.emails else None,
            phone_number=user.phone_numbers[0].phone_number
            if user.phone_numbers
            else None,
            profile_picture=user.profile_picture.profile_picture
            if user.profile_picture
            else None,
            creator_id=user.user_info.creator_id if user.user_info else None,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_activated=user.is_activated,
            is_archived=user.is_archived,
            role=Role(user.role).name,
            signup_platform=SignUpPlatform(user.signup_platform).name,
        )


class LoginResponseModel(BaseModel):
    access_token: str
    user: UserOut | None = None
    token_type: str = "bearer"
    refresh_token: str
