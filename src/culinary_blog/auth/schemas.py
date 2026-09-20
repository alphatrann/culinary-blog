import re
import uuid
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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


class UserOut(BaseModel):
    """Build with `UserOut.model_validate(user)`; never exposes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    email: str
    avatar_url: str | None
    roles: list[str]


@dataclass(frozen=True)
class AuthSession:
    """Result of a successful register/login/refresh: the user plus raw tokens for the router to put in cookies."""

    user: UserOut
    access_token: str
    refresh_token: str
