"""
Shared Pytest Fixtures for Backend Tests.
Provides isolated in-memory SQLite database sessions.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import backend.app.models  # noqa: F401
from backend.app.db.base import Base


@pytest.fixture
def db_session() -> Session:
    """Isolated in-memory SQLite database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session: Session):
    """FastAPI TestClient with isolated in-memory SQLite database dependency override."""
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.db.session import get_db_session

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def anyio_backend():
    """Specify asyncio as the default backend for anyio test execution."""
    return "asyncio"


@pytest.fixture
async def async_client(db_session: Session):
    """Asynchronous HTTP client using httpx.AsyncClient with in-memory SQLite database override."""
    from httpx import ASGITransport, AsyncClient
    from backend.app.main import app
    from backend.app.db.session import get_db_session

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
