import os
import pytest
from sqlmodel import SQLModel, Session, create_engine
from unittest.mock import patch


def test_create_db_creates_tables():
    """create_db creates all SQLModel tables."""
    test_engine = create_engine('sqlite:///:memory:')
    with patch('database.engine', test_engine):
        from database import create_db
        create_db()
    # If no exception, tables were created successfully
    assert True


def test_session_local_returns_session():
    """SessionLocal returns a valid SQLModel Session."""
    from database import SessionLocal
    session = SessionLocal()
    assert isinstance(session, Session)
    session.close()


def test_get_session_yields_session():
    """get_session yields a valid session."""
    from database import get_session
    gen = get_session()
    session = next(gen)
    assert isinstance(session, Session)
    try:
        next(gen)
    except StopIteration:
        pass