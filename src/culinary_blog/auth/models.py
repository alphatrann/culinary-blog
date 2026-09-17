import uuid
from datetime import UTC, datetime

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, String, Text, text
from sqlmodel import Field, SQLModel

from culinary_blog.database.base import BaseModel


class User(BaseModel, table=True):
    __tablename__ = "users"

    email: str = Field(max_length=256, nullable=False, unique=True, index=True)
    password_hash: str | None = Field(default=None, max_length=256, nullable=True)
    display_name: str = Field(max_length=100, nullable=False)
    avatar_url: str | None = Field(default=None, max_length=500, nullable=True)
    bio: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    roles: list[str] = Field(
        default_factory=lambda: ["author"],
        sa_column=Column(ARRAY(String(20)), nullable=False, server_default=text("'{author}'")),
    )
    is_active: bool = Field(default=True, nullable=False)
    email_confirmed: bool = Field(default=False, nullable=False)
    google_sub: str | None = Field(default=None, max_length=255, unique=True, nullable=True)
    failed_login_count: int = Field(default=0, nullable=False)
    locked_until: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))


class RefreshToken(SQLModel, table=True):
    """Not a BaseModel: no soft delete / row_version — tokens are revoked, not soft-deleted."""

    __tablename__ = "refresh_tokens"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    user_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    token_hash: str = Field(max_length=64, nullable=False, unique=True, index=True)
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    revoked_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    replaced_by_token_hash: str | None = Field(default=None, max_length=64, nullable=True)
    created_by_ip: str | None = Field(default=None, max_length=45, nullable=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
    )
