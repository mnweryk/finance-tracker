from unittest.mock import Mock, patch

import pytest

from db.connection import DatabaseConnection
from db.db_config import DatabaseConfig


def test_init_creates_schema_and_session_factory() -> None:
    """Initialize the engine, schema, and configured session factory."""
    engine = Mock(name="engine")
    session_factory = Mock(name="session_factory")
    config = DatabaseConfig(host="localhost", port=5432, name="finance")

    with (
        patch.object(DatabaseConnection, "create_engine", return_value=engine),
        patch("db.connection.Base.metadata.create_all") as create_all,
        patch("db.connection.sessionmaker", return_value=session_factory) as make_session,
    ):
        connection = DatabaseConnection(config, init_db=True)

    assert connection.engine is engine
    assert connection.SessionLocal is session_factory
    create_all.assert_called_once_with(engine)
    make_session.assert_called_once_with(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


def test_create_engine_uses_postgres_environment_credentials() -> None:
    """Build the PostgreSQL engine from config and environment credentials."""
    config = DatabaseConfig(host="db.example", port=5433, name="finance")
    database_url = Mock(name="database_url")
    engine = Mock(name="engine")

    with (
        patch.dict("os.environ", {"POSTGRES_USER": "test-user", "POSTGRES_PASSWORD": "test-password"}),
        patch("db.connection.URL.create", return_value=database_url) as create_url,
        patch("db.connection.create_engine", return_value=engine) as make_engine,
    ):
        connection = object.__new__(DatabaseConnection)
        result = connection.create_engine(config)

    assert result is engine
    create_url.assert_called_once_with(
        drivername="postgresql",
        username="test-user",
        password="test-password",
        host="db.example",
        port=5433,
        database="finance",
    )
    make_engine.assert_called_once_with(database_url)


def test_get_session_commits_and_closes_session() -> None:
    """Commit successful work and close the session."""
    session = Mock(name="session")
    connection = object.__new__(DatabaseConnection)
    connection.SessionLocal = Mock(return_value=session)

    with connection.get_session() as active_session:
        assert active_session is session

    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()
    session.close.assert_called_once_with()


def test_get_session_rolls_back_and_closes_on_error() -> None:
    """Roll back failed work, close the session, and re-raise the error."""
    session = Mock(name="session")
    connection = object.__new__(DatabaseConnection)
    connection.SessionLocal = Mock(return_value=session)

    with pytest.raises(RuntimeError, match="database operation failed"):
        with connection.get_session():
            raise RuntimeError("database operation failed")

    session.commit.assert_not_called()
    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()
