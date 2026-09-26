"""Import job queue and workers."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import valkey
from pydantic import BaseModel

from app.config import settings
from services.lance_store import get_lance_store

logger = logging.getLogger(__name__)


class ImportJob(BaseModel):
    """Import job model."""

    id: str
    dataset_id: str
    format: str  # jsonl, parquet, csv, hf
    source: str  # file path, s3 uri, hf dataset id
    status: str  # queued, running, completed, failed
    progress: float = 0.0
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None
    records_imported: int = 0


class ImportJobQueue:
    """Import job queue using Valkey."""

    def __init__(self):
        self.redis = valkey.from_url(settings.redis_url)
        self.queue_key = "import:queue"
        self.jobs_key = "import:jobs"

    async def enqueue(self, job: ImportJob) -> str:
        """Enqueue an import job."""
        job_id = job.id
        
        # Store job metadata
        self.redis.hset(
            f"{self.jobs_key}:{job_id}",
            mapping={
                "dataset_id": job.dataset_id,
                "format": job.format,
                "source": job.source,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
            },
        )
        
        # Add to queue
        self.redis.lpush(self.queue_key, job_id)
        
        return job_id

    async def dequeue(self) -> str | None:
        """Dequeue the next job."""
        return self.redis.rpop(self.queue_key)

    async def get_job(self, job_id: str) -> dict | None:
        """Get job metadata."""
        return self.redis.hgetall(f"{self.jobs_key}:{job_id}")

    async def update_job(self, job_id: str, **kwargs) -> None:
        """Update job status."""
        self.redis.hset(f"{self.jobs_key}:{job_id}", mapping=kwargs)


async def process_import_job(job_id: str, queue: ImportJobQueue) -> None:
    """Process an import job."""
    job_data = await queue.get_job(job_id)
    if not job_data:
        logger.error(f"Job not found: {job_id}")
        return

    # Update status
    await queue.update_job(job_id, status="running", started_at=datetime.utcnow().isoformat())

    try:
        dataset_id = job_data["dataset_id"]
        source = job_data["source"]
        format_type = job_data["format"]

        # Get Lance store
        store = get_lance_store(dataset_id)

        # Import based on format
        records = await _import_from_source(source, format_type)

        # Append to Lance dataset
        if records:
            store.append(records)

        await queue.update_job(
            job_id,
            status="completed",
            finished_at=datetime.utcnow().isoformat(),
            records_imported=len(records),
            progress=100.0,
        )

        logger.info(f"Import completed: {job_id} - {len(records)} records")

    except Exception as e:
        logger.error(f"Import failed: {job_id} - {e}")
        await queue.update_job(
            job_id,
            status="failed",
            finished_at=datetime.utcnow().isoformat(),
            error=str(e),
        )


async def _import_from_source(source: str, format_type: str) -> List[dict]:
    """Import records from source based on format."""
    import pandas as pd

    records = []

    if format_type == "jsonl":
        # TODO: Implement JSONL import
        pass
    elif format_type == "parquet":
        # TODO: Implement Parquet import
        pass
    elif format_type == "csv":
        df = pd.read_csv(source)
        records = df.to_dict("records")
    elif format_type == "hf":
        # TODO: Implement HF dataset import
        pass

    return records


async def start_import_worker():
    """Start the import job worker."""
    queue = ImportJobQueue()

    logger.info("Import worker started")

    while True:
        try:
            job_id = await queue.dequeue()
            if job_id:
                await process_import_job(job_id, queue)
            else:
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(1)
