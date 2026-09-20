import uuid
from datetime import UTC, datetime

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import col, select

from culinary_blog.auth.models import RefreshToken, User
from culinary_blog.errors import ConflictError

UNIQUE_VIOLATION = "23505"  # PostgreSQL SQLSTATE


class AuthRepository:
    """The only place that runs auth queries. Multi-step writes are single methods so they commit atomically."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_user_by_email(self, email: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(select(User).where(User.email == email, col(User.is_deleted).is_(False)))
            return result.scalars().first()

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(select(User).where(User.id == user_id, col(User.is_deleted).is_(False)))
            return result.scalars().first()

    async def create_user_with_refresh_token(self, user: User, token: RefreshToken) -> None:
        async with self._session_factory() as session:
            session.add(user)
            try:
                await session.flush()  # no ORM relationship links the two, so order the inserts explicitly (FK)
                session.add(token)
                await session.commit()
            except IntegrityError as exc:
                if getattr(exc.orig, "sqlstate", None) != UNIQUE_VIOLATION:
                    raise
                raise ConflictError(
                    "Email is already registered"
                ) from exc  # the only unique column set on registration is email

    async def save_login_state(self, user: User) -> None:
        """Persists failed-login / lockout counters."""
        async with self._session_factory() as session:
            user.updated_at = datetime.now(UTC)
            user.row_version += 1
            await session.merge(user)
            await session.commit()

    async def add_refresh_token(self, token: RefreshToken) -> None:
        async with self._session_factory() as session:
            session.add(token)
            await session.commit()

    async def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        async with self._session_factory() as session:
            result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
            return result.scalars().first()

    async def rotate_refresh_token(self, old_hash: str, new_token: RefreshToken) -> bool:
        """Atomically revokes `old_hash` (only if still active) and stores its replacement.

        Returns False when another request already consumed the token, so a replay never yields two live tokens.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                update(RefreshToken)
                .where(col(RefreshToken.token_hash) == old_hash, col(RefreshToken.revoked_at).is_(None))
                .values(revoked_at=datetime.now(UTC), replaced_by_token_hash=new_token.token_hash)
            )
            if result.rowcount == 0:  # type: ignore[attr-defined]
                await session.rollback()
                return False
            session.add(new_token)
            await session.commit()
            return True

    async def revoke_refresh_token(self, token_hash: str) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(RefreshToken)
                .where(col(RefreshToken.token_hash) == token_hash, col(RefreshToken.revoked_at).is_(None))
                .values(revoked_at=datetime.now(UTC))
            )
            await session.commit()

    async def revoke_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(RefreshToken)
                .where(col(RefreshToken.user_id) == user_id, col(RefreshToken.revoked_at).is_(None))
                .values(revoked_at=datetime.now(UTC))
            )
            await session.commit()
