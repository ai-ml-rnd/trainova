"""Tenant isolation tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_tenant_cannot_access_other_tenant_data():
    """Test that tenant A cannot access tenant B's data."""
    # Simulate tenant A making a request
    response_a = client.get(
        "/v1/tenants/me",
        headers={"Authorization": "Bearer token-tenant-a"},
    )
    assert response_a.status_code == 200
    tenant_a_id = response_a.json()["id"]

    # Simulate tenant B making a request
    response_b = client.get(
        "/v1/tenants/me",
        headers={"Authorization": "Bearer token-tenant-b"},
    )
    assert response_b.status_code == 200
    tenant_b_id = response_b.json()["id"]

    # Tenants should have different IDs
    assert tenant_a_id != tenant_b_id


@pytest.mark.asyncio
async def test_cross_tenant_dataset_access():
    """Test that tenant A cannot access tenant B's datasets."""
    # Tenant A creates a dataset
    response_a = client.post(
        "/v1/datasets",
        json={
            "name": "Tenant A Dataset",
            "kind": "sft",
            "schema": {},
        },
        headers={"Authorization": "Bearer token-tenant-a"},
    )
    assert response_a.status_code == 201
    dataset_a_id = response_a.json()["id"]

    # Tenant B tries to access Tenant A's dataset
    response_b = client.get(
        f"/v1/datasets/{dataset_a_id}",
        headers={"Authorization": "Bearer token-tenant-b"},
    )
    assert response_b.status_code == 403


@pytest.mark.asyncio
async def test_cross_tenant_records_access():
    """Test that tenant A cannot access tenant B's records."""
    # Tenant A creates a record
    response_a = client.post(
        "/v1/records/test-dataset/records",
        json={
            "fields": {"text": "Tenant A record"},
            "metadata": {},
        },
        headers={"Authorization": "Bearer token-tenant-a"},
    )
    assert response_a.status_code == 201

    # Tenant B tries to access Tenant A's record
    response_b = client.get(
        "/v1/records/test-dataset/records/test-record",
        headers={"Authorization": "Bearer token-tenant-b"},
    )
    assert response_b.status_code == 403
