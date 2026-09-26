"""Test fixtures and configuration."""

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Database session fixture."""
    from app.dependencies import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def override_settings():
    """Override settings fixture."""

    def _override(**kwargs):
        for key, value in kwargs.items():
            setattr(settings, key, value)

    return _override
