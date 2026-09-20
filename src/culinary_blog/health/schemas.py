from typing import Literal, Self

from pydantic import BaseModel

Status = Literal["healthy", "unhealthy"]


class HealthEntry(BaseModel):
    status: Status
    detail: str | None = None


class HealthReport(BaseModel):
    status: Status
    entries: dict[str, HealthEntry]

    @classmethod
    def from_entries(cls, entries: dict[str, HealthEntry]) -> Self:
        healthy = all(entry.status == "healthy" for entry in entries.values())
        return cls(status="healthy" if healthy else "unhealthy", entries=entries)
