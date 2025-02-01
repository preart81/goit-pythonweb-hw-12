""" Database connection and session manager """

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Manages the creation and lifecycle of database sessions using SQLAlchemy.
    Attributes:
        _engine (AsyncEngine | None): The asynchronous engine for database connections.
        _session_maker (async_sessionmaker): The session maker for creating new sessions.
    Methods:
        __init__(url: str):
            Initializes the DatabaseSessionManager with the given database URL.
        session():
            Asynchronous context manager that provides a database session.
            Yields:
                session: An active database session.
            Raises:
                RuntimeError: If the session maker is not initialized.
                SQLAlchemyError: If an error occurs during the session, it will
                be rolled back and re-raised.
    """

    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provides a database session for executing database operations.

        This method is an asynchronous generator that yields a database session.
        If the session maker is not initialized, it raises a RuntimeError.
        If an SQLAlchemyError occurs during the session, it rolls back the session
        and re-raises the original error. Finally, it ensures the session is closed.

        Yields:
            session: An instance of the database session.

        Raises:
            RuntimeError: If the session maker is not initialized.
            SQLAlchemyError: If an error occurs during the session.
        """
        if self._session_maker is None:
            raise RuntimeError("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Asynchronous generator function that provides a database session.

    Yields:
        AsyncSession: An asynchronous database session.
    """
    async with sessionmanager.session() as session:
        yield session
