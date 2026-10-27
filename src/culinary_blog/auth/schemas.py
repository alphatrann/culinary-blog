import re
import uuid
from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator


class RegisterRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=100)
    email: EmailStr = Field(max_length=256)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("display_name")
    @classmethod
    def _strip_display_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("display_name must be at least 2 characters")
        return value

    @field_validator("password")
    @classmethod
    def _strong_password(cls, value: str) -> str:
        if not (re.search(r"[A-Z]", value) and re.search(r"\d", value) and re.search(r"[^A-Za-z0-9]", value)):
            raise ValueError("password must contain an uppercase letter, a digit and a special character")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=1, max_length=4096)


class ProfileUpdateRequest(BaseModel):
    """PATCH body: only the fields sent are changed (`model_dump(exclude_unset=True)`). `email` is not accepted."""

    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, max_length=100)
    avatar_url: HttpUrl | None = None
    bio: str | None = Field(default=None, max_length=1000)

    @field_validator("display_name")
    @classmethod
    def _clean_display_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("display_name cannot be null")
        value = value.strip()
        if len(value) < 2:
            raise ValueError("display_name must be at least 2 characters")
        return value

    @field_validator("avatar_url")
    @classmethod
    def _avatar_fits_column(cls, value: HttpUrl | None) -> HttpUrl | None:
        if value is not None and len(str(value)) > 500:
            raise ValueError("avatar_url must be at most 500 characters")
        return value


class UserOut(BaseModel):
    """Build with `UserOut.model_validate(user)`; never exposes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    email: str
    avatar_url: str | None
    bio: str | None
    roles: list[str]
    email_confirmed: bool
    created_at: datetime


@dataclass(frozen=True)
class AuthSession:
    """Result of a successful register/login/refresh: the user plus raw tokens for the router to put in cookies."""

    user: UserOut
    access_token: str
    refresh_token: str
