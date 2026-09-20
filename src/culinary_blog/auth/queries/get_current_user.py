from dataclasses import dataclass

from culinary_blog.auth.principal import Principal
from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.schemas import UserOut
from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.errors import UnauthorizedError


@dataclass(frozen=True)
class GetCurrentUserQuery(Query):
    actor: Principal


class GetCurrentUserHandler(QueryHandler[GetCurrentUserQuery, UserOut]):
    """Resolves the token's subject to a live user; a deleted/deactivated account is treated as logged out."""

    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetCurrentUserQuery) -> UserOut:
        user = await self._repository.get_user_by_id(query.actor.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Account no longer available")
        return UserOut.model_validate(user)
