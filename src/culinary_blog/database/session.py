from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from culinary_blog.config import get_settings

settings = get_settings()

DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 40

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=settings.db_pool_pre_ping,
    pool_recycle=settings.db_pool_recycle_seconds,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Pure reads run in AUTOCOMMIT on the same pool: no BEGIN/ROLLBACK round trips around every query. Traces of the M6a
# stress run showed ~10 DB round trips per category-detail request, half of them transaction control.
read_session_factory = async_sessionmaker(
    engine.execution_options(isolation_level="AUTOCOMMIT"), expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
