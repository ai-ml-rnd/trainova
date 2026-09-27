"""Import job endpoints."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import current_tenant, db
from models.import_job import ImportJob, ImportJobStatus, SourceType
from core.import_worker import ImportWorker

from api.v1.schemas import (
    ImportJobCreate,
    ImportJobResponse,
)

router = APIRouter()


@router.post("", response_model=ImportJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_import_job(
    job: ImportJobCreate,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Create an import job."""
    # Validate dataset exists and belongs to tenant
    # TODO: Implement dataset validation
    
    # Create import job
    import_job = ImportJob(
        id=uuid.uuid4(),
        dataset_id=uuid.UUID(job.dataset_id),
        source_type=SourceType(job.source_type),
        source_path=job.source_path,
        status=ImportJobStatus.QUEUED,
        created_at=datetime.utcnow(),
    )
    
    session.add(import_job)
    await session.commit()
    await session.refresh(import_job)
    
    # TODO: Enqueue job for worker processing
    
    return ImportJobResponse(
        id=str(import_job.id),
        dataset_id=str(import_job.dataset_id),
        source_type=import_job.source_type.value,
        source_path=import_job.source_path,
        status=import_job.status.value,
        progress=import_job.progress,
        created_at=import_job.created_at.isoformat(),
    )


@router.get("/{job_id}", response_model=ImportJobResponse)
async def get_import_job(
    job_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Get import job status."""
    stmt = select(ImportJob).where(ImportJob.id == uuid.UUID(job_id))
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()
    
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found",
        )
    
    return ImportJobResponse(
        id=str(job.id),
        dataset_id=str(job.dataset_id),
        source_type=job.source_type.value,
        source_path=job.source_path,
        status=job.status.value,
        progress=job.progress,
        rows_imported=job.rows_imported,
        total_rows=job.total_rows,
        error=job.error,
        created_at=job.created_at.isoformat() if job.created_at else None,
        started_at=job.started_at.isoformat() if job.started_at else None,
        finished_at=job.finished_at.isoformat() if job.finished_at else None,
    )


@router.post("/{job_id}:cancel", response_model=ImportJobResponse)
async def cancel_import_job(
    job_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Cancel an import job."""
    stmt = select(ImportJob).where(ImportJob.id == uuid.UUID(job_id))
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()
    
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found",
        )
    
    if job.status not in [ImportJobStatus.QUEUED, ImportJobStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel job in status: {job.status.value}",
        )
    
    job.status = ImportJobStatus.CANCELLED
    job.finished_at = datetime.utcnow()
    await session.commit()
    await session.refresh(job)
    
    return ImportJobResponse(
        id=str(job.id),
        dataset_id=str(job.dataset_id),
        source_type=job.source_type.value,
        source_path=job.source_path,
        status=job.status.value,
        progress=job.progress,
        error=job.error,
        created_at=job.created_at.isoformat() if job.created_at else None,
        started_at=job.started_at.isoformat() if job.started_at else None,
        finished_at=job.finished_at.isoformat() if job.finished_at else None,
    )


@router.get("/{job_id}/events")
async def get_import_job_events(
    job_id: str,
    last_event_id: Optional[str] = None,
    session=Depends(db),
):
    """Get import job progress events (SSE)."""
    # TODO: Implement SSE stream from Valkey
    # For now, return static response
    return {
        "job_id": job_id,
        "events": [],
    }
