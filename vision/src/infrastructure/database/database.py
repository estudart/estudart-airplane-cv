from typing import Iterator

from sqlalchemy import Connection, create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from contextlib import contextmanager


class Base(DeclarativeBase):
    """Root of all ORM table mappings. ORM models (infrastructure/database/tables) subclass this."""


class Database:
    def __init__(self, url: str):
        self._engine = create_engine(
            url,
            pool_pre_ping=True,
            future=True
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            expire_on_commit=False
        )

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Yield a transactional session: commit on success, roll back on error, always close."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
