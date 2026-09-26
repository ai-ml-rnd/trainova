"""Test that generic CRUD passthrough endpoints are not allowed."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_no_generic_table_crud():
    """Test that generic CRUD endpoints are not available."""
    # Try to access generic CRUD endpoints
    response = client.get("/v1/tables/datasets")
    assert response.status_code == 404

    response = client.post("/v1/tables/datasets/create")
    assert response.status_code == 404

    response = client.put("/v1/tables/datasets/record")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_no_db_query_passthrough():
    """Test that raw SQL query endpoints are not available."""
    response = client.post("/v1/db/query", json={"query": "SELECT * FROM datasets"})
    assert response.status_code == 404

    response = client.post("/v1/db/raw", json={"sql": "DELETE FROM datasets"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_no_s3_admin_endpoints():
    """Test that S3 admin endpoints are not accessible from browser."""
    response = client.get("/v1/s3/buckets")
    assert response.status_code == 404

    response = client.post("/v1/s3/create-bucket", json={"name": "test-bucket"})
    assert response.status_code == 404
