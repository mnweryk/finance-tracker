import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from .db_config import DatabaseConfig
from .models import Base


class DatabaseConnection:
    """
    A class to manage the database connection using SQLAlchemy.

    Attributes:
        engine: The SQLAlchemy engine instance.
        SessionLocal: The session factory instance.
    """

    def __init__(self, db_config: DatabaseConfig, init_db: bool = False):
        """
        Initializes the DatabaseConnection with the provided database configuration.

        Args:
            db_config (DatabaseConfig): The database configuration object.
            init_db (bool): Whether to initialize the database tables.
            
        """
        self.engine = self.create_engine(db_config)
        if init_db:
            self.init_db()
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    def init_db(self):
        """
        Initializes the database by creating all tables defined in the SQLAlchemy models.
        """
        Base.metadata.create_all(self.engine)

    def create_engine(self, db_config: DatabaseConfig):
        """
        Creates a SQLAlchemy engine based on the provided database configuration.

        Args:
            db_config (DatabaseConfig): The database configuration object.

        Returns:
            sqlalchemy.engine.Engine: The created SQLAlchemy engine.
        """
        db_user = os.getenv("POSTGRES_USER", "user")
        db_password = os.getenv("POSTGRES_PASSWORD", "password")

        database_url = URL.create(
            drivername="postgresql",
            username=db_user,
            password=db_password,
            host=db_config.host,
            port=db_config.port,
            database=db_config.name,
        )

        return create_engine(database_url)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provides a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
