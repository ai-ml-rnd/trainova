"""Tenant management endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import current_tenant
from api.v1.schemas import TenantResponse

router = APIRouter()


@router.get("/me", response_model=TenantResponse)
async def get_my_tenant(tenant_id: str = Depends(current_tenant)):
    """Get current tenant information."""
    # In production, fetch tenant from database
    return TenantResponse(
        id=tenant_id,
        slug="default",
        name="Default Tenant",
        created_at="2026-01-01T00:00:00Z",
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str):
    """Get tenant by ID."""
    # In production, fetch tenant from database
    return TenantResponse(
        id=tenant_id,
        slug="default",
        name="Default Tenant",
        created_at="2026-01-01T00:00:00Z",
    )
