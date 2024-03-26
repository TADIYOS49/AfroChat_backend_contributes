from enum import Enum
from datetime import datetime
from uuid import UUID
from app.routers.api_v1.Auth.models import Role, User

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserCreateAdmin(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=50)
    phone_number: str | None = None
    role: str


class UpdateUserProfileAdmin(BaseModel):
    user_id: UUID
    username: str | None = Field(None, max_length=50)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    profile_picture: HttpUrl | None = None
    new_password: str | None = None


class CompleteRegistration(BaseModel):
    email: EmailStr
    password: str


class OrderBy(str, Enum):
    USERNAME_ASC = "username_asc"
    USERNAME_DESC = "username_desc"
    ROLE_ASC = "role_asc"
    ROLE_DESC = "role_desc"
    REGISTRATION_DATE_ASC = "registration_date_asc"
    REGISTRATION_DATE_DESC = "registration_date_desc"
