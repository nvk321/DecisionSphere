"""
Database Engine and Session Factory.
"""
from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings

settings = get_settings()

# Engine creation with pool pre-ping to detect stale/dropped connections
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a transactional SQLAlchemy session.
    Automatically closes session on request completion.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
