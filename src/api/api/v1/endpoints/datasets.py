"""Dataset endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.dependencies import current_tenant, db

from api.v1.schemas import DatasetResponse, DatasetListResponse

router = APIRouter()


class DatasetCreate(BaseModel):
    """Create dataset request."""

    name: str = Field(..., min_length=1, max_length=100)
    kind: str = Field(..., pattern="^(pretrain|sft|preference|vlm|eval|generic)$")
    schema: dict = Field(default_factory=dict)


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset: DatasetCreate,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Create a new dataset."""
    # TODO: Implement dataset creation
    return DatasetResponse(
        id="test-dataset-id",
        name=dataset.name,
        kind=dataset.kind,
        created_at="2026-09-26T00:00:00Z",
    )


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    limit: int = 50,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """List datasets for the current tenant."""
    # TODO: Implement dataset listing
    return DatasetListResponse(
        datasets=[],
        pagination={"page": 1, "page_size": limit, "total": 0},
    )


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Get dataset by ID."""
    # TODO: Implement dataset retrieval
    return DatasetResponse(
        id=dataset_id,
        name="Test Dataset",
        kind="sft",
        created_at="2026-09-26T00:00:00Z",
    )


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    dataset: DatasetCreate,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Update dataset."""
    # TODO: Implement dataset update
    return DatasetResponse(
        id=dataset_id,
        name=dataset.name,
        kind=dataset.kind,
        created_at="2026-09-26T00:00:00Z",
    )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Delete dataset."""
    # TODO: Implement dataset deletion
    return None
