"""Import job endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.dependencies import current_tenant, db

from jobs.import_jobs import ImportJob, ImportJobQueue

router = APIRouter()


class ImportJobCreate(BaseModel):
    """Create import job request."""

    dataset_id: str
    format: str = Field(..., pattern="^(jsonl|parquet|csv|hf)$")
    source: str = Field(..., description="Source path/URI/ID")


class ImportJobResponse(BaseModel):
    """Import job response."""

    id: str
    dataset_id: str
    format: str
    source: str
    status: str
    progress: float
    created_at: str


@router.post("", response_model=ImportJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_import_job(
    job: ImportJobCreate,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Create an import job."""
    import uuid
    from datetime import datetime

    import_job = ImportJob(
        id=str(uuid.uuid4()),
        dataset_id=job.dataset_id,
        format=job.format,
        source=job.source,
        status="queued",
        created_at=datetime.utcnow(),
    )

    queue = ImportJobQueue()
    job_id = await queue.enqueue(import_job)

    return ImportJobResponse(
        id=job_id,
        dataset_id=job.dataset_id,
        format=job.format,
        source=job.source,
        status="queued",
        progress=0.0,
        created_at=import_job.created_at.isoformat(),
    )


@router.get("/{job_id}", response_model=ImportJobResponse)
async def get_import_job(
    job_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Get import job status."""
    queue = ImportJobQueue()
    job_data = await queue.get_job(job_id)

    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return ImportJobResponse(
        id=job_id,
        dataset_id=job_data["dataset_id"],
        format=job_data["format"],
        source=job_data["source"],
        status=job_data["status"],
        progress=float(job_data.get("progress", 0)),
        created_at=job_data["created_at"],
    )


@router.get("", response_model=list[ImportJobResponse])
async def list_import_jobs(
    limit: int = 50,
    status: str | None = None,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """List import jobs."""
    # TODO: Implement job listing
    return []
