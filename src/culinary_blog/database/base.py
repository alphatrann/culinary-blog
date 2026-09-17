import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, text
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Shared columns for every entity: UUID PK, audit timestamps, soft delete, optimistic concurrency.

    Datetime columns use `sa_type=` (not `sa_column=Column(...)`) so SQLModel builds a fresh
    Column per subclass table — a single shared Column instance can't be attached to six tables.
    """

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": text("now()")},
    )
    updated_at: datetime | None = Field(default=None, nullable=True, sa_type=DateTime(timezone=True))
    is_deleted: bool = Field(
        default=False,
        nullable=False,
        index=True,
        sa_column_kwargs={"server_default": text("false")},
    )
    row_version: int = Field(
        default=0,
        nullable=False,
        sa_column_kwargs={"server_default": text("0")},
    )
