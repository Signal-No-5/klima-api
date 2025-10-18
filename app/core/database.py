from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from app.core.prefs import DatabaseSettings


class Database:
    """
    Encapsulates multiple DB engines and sessions for SQLModel.
    Supports creating all tables and context-managed sessions.
    """

    def __init__(self, settings: DatabaseSettings, metadata: type[SQLModel]):
        self.settings = settings
        self.metadata = metadata
        self.engines: Dict[str, Any] = {}
        self.sessions: Dict[str, sessionmaker] = {}

        for name, config in settings.databases.items():
            engine = create_engine(config.url, future=True)
            self.engines[name] = engine
            self.sessions[name] = sessionmaker(
                autocommit=False, autoflush=False, bind=engine
            )

    @asynccontextmanager
    async def get_db(self) -> AsyncGenerator[Dict[str, Session], None]:
        """
        Provides a dict of {db_name: Session} for all configured databases.
        """
        sessions = {name: factory() for name, factory in self.sessions.items()}
        try:
            yield sessions
            # Commit all writes
            for session in sessions.values():
                session.commit()
        except Exception:
            # Rollback all on error
            for session in sessions.values():
                session.rollback()
            raise
        finally:
            for session in sessions.values():
                session.close()

    def drop_all(self):
        for engine in self.engines.values():
            self.metadata.metadata.drop_all(bind=engine)

    def create_all(self):
        """Create all tables in every configured database."""
        self.drop_all
        for engine in self.engines.values():
            self.metadata.metadata.create_all(bind=engine)
