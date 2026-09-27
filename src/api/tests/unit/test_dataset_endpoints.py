"""Unit tests for dataset endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.dependencies import Base, get_db
from app.main import app
from models.dataset import Dataset, Tenant, User, Workspace


@pytest.fixture
def async_engine():
    """Create async engine for testing."""
    return create_async_engine(
        "postgresql+asyncpg://forge:forge@localhost:5432/forge_test",
        echo=True,
    )


@pytest.fixture
async def setup_test_db(async_engine):
    """Set up test database."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(setup_test_db):
    """Create test client."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_dataset(client, async_engine):
    """Test creating a new dataset."""
    # Create tenant
    async with async_engine.begin() as conn:
        await conn.execute(
            text(
                """
                INSERT INTO tenants (id, slug, name, created_at)
                VALUES (:id, :slug, :name, :now)
                """
            ),
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "slug": "test-tenant",
                "name": "Test Tenant",
                "now": "2026-09-26T00:00:00Z",
            },
        )
        await conn.execute(
            text(
                """
                INSERT INTO workspaces (id, tenant_id, name)
                VALUES (:id, :tenant_id, :name)
                """
            ),
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "tenant_id": "00000000-0000-0000-0000-000000000000",
                "name": "Test Workspace",
            },
        )
        await conn.commit()

    response = client.post(
        "/v1/datasets",
        json={
            "name": "Test Dataset",
            "kind": "sft",
            "workspace_id": "11111111-1111-1111-1111-111111111111",
        },
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Dataset"
    assert data["kind"] == "sft"


@pytest.mark.asyncio
async def test_list_datasets(client, async_engine):
    """Test listing datasets."""
    response = client.get(
        "/v1/datasets",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert "pagination" in data
