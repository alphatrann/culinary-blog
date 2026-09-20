import uuid
from dataclasses import dataclass

ADMIN_ROLE = "admin"


@dataclass(frozen=True)
class Principal:
    """The authenticated caller, as carried by a verified access token."""

    user_id: uuid.UUID
    roles: tuple[str, ...]

    @property
    def is_admin(self) -> bool:
        return ADMIN_ROLE in self.roles
