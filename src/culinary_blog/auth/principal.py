import uuid
from dataclasses import dataclass

ADMIN_ROLE = "admin"
AUTHOR_ROLE = "author"


@dataclass(frozen=True)
class Principal:
    """The authenticated caller, as carried by a verified access token."""

    user_id: uuid.UUID
    roles: tuple[str, ...]

    @property
    def is_admin(self) -> bool:
        return ADMIN_ROLE in self.roles

    @property
    def can_write_recipes(self) -> bool:
        return self.is_admin or AUTHOR_ROLE in self.roles
