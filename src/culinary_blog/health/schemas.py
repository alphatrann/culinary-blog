from typing import Literal

from pydantic import BaseModel

Status = Literal["healthy", "unhealthy"]


class HealthEntry(BaseModel):
    status: Status
    detail: str | None = None


class HealthReport(BaseModel):
    status: Status
    entries: dict[str, HealthEntry]
