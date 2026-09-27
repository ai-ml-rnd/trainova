"""Record endpoints."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import current_tenant, db
from core.record_store import Record, ScanResult
from core.postgres_record_store import PostgresRecordStore

from api.v1.schemas import (
    RecordCreate,
    RecordResponse,
    BulkRecordResponse,
    FilterRequest,
    SemanticSearchRequest,
)

router = APIRouter()


@router.post("/{dataset_id}:bulk", response_model=BulkRecordResponse)
async def bulk_add_records(
    dataset_id: str,
    records: List[RecordCreate],
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Add records to a dataset.
    
    Args:
        dataset_id: The dataset ID
        records: List of records to add (max 10k)
        tenant_id: Tenant ID from token
        
    Returns:
        BulkRecordResponse with number of records added
    """
    # Validate record count
    if len(records) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add more than 10,000 records at once",
        )
    
    # Convert to domain records
    domain_records = [
        Record(
            record_id=r.record_id,
            fields=r.fields,
            metadata=r.metadata or {},
            provenance=r.provenance or [],
            quality=r.quality or {},
            status=r.status or "pending",
            reject_reason=r.reject_reason,
            embedding=r.embedding,
        )
        for r in records
    ]
    
    # Add records
    store = PostgresRecordStore(session)
    added = await store.bulk_add(dataset_id, domain_records)
    
    return BulkRecordResponse(added=added)


@router.get("/{dataset_id}/records/{record_id}", response_model=RecordResponse)
async def get_record(
    dataset_id: str,
    record_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Get a record by ID."""
    store = PostgresRecordStore(session)
    record = await store.get_by_id(dataset_id, record_id)
    
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )
    
    return RecordResponse(
        record_id=record.record_id,
        fields=record.fields,
        metadata=record.metadata,
        provenance=record.provenance,
        quality=record.quality,
        status=record.status,
        reject_reason=record.reject_reason,
        embedding=record.embedding,
    )


@router.get("/{dataset_id}/records", response_model=List[RecordResponse])
async def scan_records(
    dataset_id: str,
    cursor: Optional[str] = None,
    limit: int = 100,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Scan records in a dataset."""
    if limit > 1000:
        limit = 1000
    
    store = PostgresRecordStore(session)
    result = await store.scan(dataset_id, cursor=cursor, limit=limit)
    
    return [
        RecordResponse(
            record_id=r.record_id,
            fields=r.fields,
            metadata=r.metadata,
            provenance=r.provenance,
            quality=r.quality,
            status=r.status,
            reject_reason=r.reject_reason,
            embedding=r.embedding,
        )
        for r in result.records
    ]


@router.post("/{dataset_id}/records:search", response_model=List[RecordResponse])
async def filter_records(
    dataset_id: str,
    filter_req: FilterRequest,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Search records using filter DSL."""
    store = PostgresRecordStore(session)
    records = await store.filter(dataset_id, filter_req.filter, limit=filter_req.limit)
    
    return [
        RecordResponse(
            record_id=r.record_id,
            fields=r.fields,
            metadata=r.metadata,
            provenance=r.provenance,
            quality=r.quality,
            status=r.status,
            reject_reason=r.reject_reason,
            embedding=r.embedding,
        )
        for r in records
    ]


@router.post("/{dataset_id}/records:semantic-search", response_model=List[RecordResponse])
async def semantic_search_records(
    dataset_id: str,
    vector: List[float],
    k: int = 10,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Semantic search for similar records."""
    store = PostgresRecordStore(session)
    records = await store.semantic_search(dataset_id, vector, k=k)
    
    return [
        RecordResponse(
            record_id=r.record_id,
            fields=r.fields,
            metadata=r.metadata,
            provenance=r.provenance,
            quality=r.quality,
            status=r.status,
            reject_reason=r.reject_reason,
            embedding=r.embedding,
        )
        for r in records
    ]
