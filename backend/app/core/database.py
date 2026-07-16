from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Supabase PostgreSQL — pool settings for production-grade connection handling
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for declarative models
Base = declarative_base()


async def get_db():
    """
    Dependency function that yields a database session.
    Used in FastAPI routes for native DI if needed, but since we are using Repositories
    we might inject this differently.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
