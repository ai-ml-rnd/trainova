"""Dataset endpoints."""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import current_tenant, db
from models.dataset import Dataset, DatasetSchema, FieldDef, QuestionDef, Tenant, Workspace

from api.v1.schemas import (
    DatasetCreate,
    DatasetListResponse,
    DatasetResponse,
    DatasetUpdate,
)

router = APIRouter()


async def get_tenant_by_id(tenant_id: str, session: AsyncSession) -> Tenant:
    """Get tenant by ID or raise 404."""
    stmt = select(Tenant).where(Tenant.id == uuid.UUID(tenant_id))
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant


async def get_workspace_by_id(workspace_id: str, tenant_id: str, session: AsyncSession) -> Workspace:
    """Get workspace by ID and tenant, or raise 404."""
    stmt = (
        select(Workspace)
        .where(Workspace.id == uuid.UUID(workspace_id))
        .where(Workspace.tenant_id == uuid.UUID(tenant_id))
    )
    result = await session.execute(stmt)
    workspace = result.scalar_one_or_none()
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset: DatasetCreate,
    tenant_id: str = Depends(current_tenant),
    session: AsyncSession = Depends(db),
):
    """Create a new dataset."""
    # Get workspace
    workspace = await get_workspace_by_id(dataset.workspace_id, tenant_id, session)
    
    # Create dataset schema if provided
    schema_id = None
    if dataset.schema:
        schema = DatasetSchema(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            name=f"schema_{dataset.name}_{uuid.uuid4().hex[:8]}",
            created_at=datetime.utcnow(),
        )
        session.add(schema)
        await session.flush()
        schema_id = schema.id
        
        # Create field definitions
        for field in dataset.schema.get("field_defs", []):
            field_def = FieldDef(
                id=uuid.uuid4(),
                schema_id=schema.id,
                name=field["name"],
                type=field["type"],
                required=field.get("required", False),
                created_at=datetime.utcnow(),
            )
            session.add(field_def)
        
        # Create question definitions
        for question in dataset.schema.get("question_defs", []):
            question_def = QuestionDef(
                id=uuid.uuid4(),
                schema_id=schema.id,
                name=question["name"],
                type=question["type"],
                settings=question.get("settings", {}),
                required=question.get("required", False),
                created_at=datetime.utcnow(),
            )
            session.add(question_def)
    
    # Create dataset
    dataset_obj = Dataset(
        id=uuid.uuid4(),
        tenant_id=uuid.UUID(tenant_id),
        workspace_id=workspace.id,
        name=dataset.name,
        kind=dataset.kind,
        schema_id=schema_id,
        created_by=uuid.UUID(tenant_id),  # TODO: Get actual user ID from token
        created_at=datetime.utcnow(),
    )
    session.add(dataset_obj)
    await session.commit()
    await session.refresh(dataset_obj)
    
    return DatasetResponse(
        id=str(dataset_obj.id),
        name=dataset_obj.name,
        kind=dataset_obj.kind,
        schema_id=str(dataset_obj.schema_id) if dataset_obj.schema_id else None,
        lance_uri=dataset_obj.lance_uri,
        draft_lance_version=dataset_obj.draft_lance_version,
        created_at=dataset_obj.created_at.isoformat() if dataset_obj.created_at else datetime.utcnow().isoformat(),
        created_by=str(dataset_obj.created_by) if dataset_obj.created_by else tenant_id,
    )


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    limit: int = 50,
    cursor: Optional[str] = None,
    tenant_id: str = Depends(current_tenant),
    session: AsyncSession = Depends(db),
):
    """List datasets for the current tenant."""
    stmt = (
        select(Dataset)
        .where(Dataset.tenant_id == uuid.UUID(tenant_id))
        .order_by(Dataset.created_at)
        .limit(limit)
    )
    
    if cursor:
        # TODO: Implement cursor-based pagination
        pass
    
    result = await session.execute(stmt)
    datasets = result.scalars().all()
    
    return DatasetListResponse(
        datasets=[
            DatasetResponse(
                id=str(d.id),
                name=d.name,
                kind=d.kind,
                schema_id=str(d.schema_id) if d.schema_id else None,
                lance_uri=d.lance_uri,
                draft_lance_version=d.draft_lance_version,
                created_at=d.created_at.isoformat() if d.created_at else datetime.utcnow().isoformat(),
                created_by=str(d.created_by) if d.created_by else tenant_id,
            )
            for d in datasets
        ],
        pagination={
            "page": 1,
            "page_size": limit,
            "total": len(datasets),
        },
    )


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    tenant_id: str = Depends(current_tenant),
    session: AsyncSession = Depends(db),
):
    """Get dataset by ID."""
    stmt = select(Dataset).where(
        Dataset.id == uuid.UUID(dataset_id),
        Dataset.tenant_id == uuid.UUID(tenant_id),
    )
    result = await session.execute(stmt)
    dataset = result.scalar_one_or_none()
    
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    return DatasetResponse(
        id=str(dataset.id),
        name=dataset.name,
        kind=dataset.kind,
        schema_id=str(dataset.schema_id) if dataset.schema_id else None,
        lance_uri=dataset.lance_uri,
        draft_lance_version=dataset.draft_lance_version,
        created_at=dataset.created_at.isoformat() if dataset.created_at else datetime.utcnow().isoformat(),
        created_by=str(dataset.created_by) if dataset.created_by else tenant_id,
    )


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    dataset: DatasetUpdate,
    tenant_id: str = Depends(current_tenant),
    session: AsyncSession = Depends(db),
):
    """Update dataset."""
    stmt = select(Dataset).where(
        Dataset.id == uuid.UUID(dataset_id),
        Dataset.tenant_id == uuid.UUID(tenant_id),
    )
    result = await session.execute(stmt)
    dataset_obj = result.scalar_one_or_none()
    
    if dataset_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    # Update fields
    if dataset.name is not None:
        dataset_obj.name = dataset.name
    if dataset.kind is not None:
        dataset_obj.kind = dataset.kind
    if dataset.schema is not None:
        # TODO: Update schema
        pass
    
    await session.commit()
    await session.refresh(dataset_obj)
    
    return DatasetResponse(
        id=str(dataset_obj.id),
        name=dataset_obj.name,
        kind=dataset_obj.kind,
        schema_id=str(dataset_obj.schema_id) if dataset_obj.schema_id else None,
        lance_uri=dataset_obj.lance_uri,
        draft_lance_version=dataset_obj.draft_lance_version,
        created_at=dataset_obj.created_at.isoformat() if dataset_obj.created_at else datetime.utcnow().isoformat(),
        created_by=str(dataset_obj.created_by) if dataset_obj.created_by else tenant_id,
    )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    tenant_id: str = Depends(current_tenant),
    session: AsyncSession = Depends(db),
):
    """Delete dataset."""
    stmt = select(Dataset).where(
        Dataset.id == uuid.UUID(dataset_id),
        Dataset.tenant_id == uuid.UUID(tenant_id),
    )
    result = await session.execute(stmt)
    dataset = result.scalar_one_or_none()
    
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    await session.delete(dataset)
    await session.commit()
    
    return None
