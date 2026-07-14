import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base
from app.api.deps import get_db

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "JSON"

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)



import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    Override the get_db dependency to use the test database.
    """
    async def override_get_db():
        yield db_session

    from app.main import app
    from app.repositories.base import UnitOfWork
    from app.services.auth_service import AuthService
    from dependency_injector import providers

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        # app.container is now set by lifespan – override it to use the test session
        container = getattr(app, "container", None)
        if container is not None:
            container.auth_service.override(
                providers.Factory(AuthService, uow=providers.Factory(UnitOfWork, session=db_session))
            )
        yield test_client
        if container is not None:
            container.auth_service.reset_override()

    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session: AsyncSession):
    # Setup test user logic here
    pass
