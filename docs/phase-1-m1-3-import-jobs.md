# Phase 1 M1.3 Import Jobs Implementation Plan

## Overview

Implement import job system for ingesting data into datasets.

## Requirements

From tasks.md:
- Connectors: JSONL, Parquet, CSV, HF mirror, S3 prefix
- SSE progress updates
- Resumable imports (checkpointing)
- 500k-row import with SSE progress
- Worker kill during import → resume from checkpoint

## Architecture

### Import Job Flow

```
1. POST /v1/datasets/{id}/imports → 202 Accepted with run_id
2. Arq worker processes batches
3. SSE: {"event": "progress", "data": {"rows": 50000, "total": 500000}}
4. On completion: SSE {"event": "completed", "data": {"records": 500000}}
```

### Import Job States

- `queued`: Job submitted, waiting for worker
- `running`: Job is processing
- `waiting_approval`: Paused for human approval (future)
- `succeeded`: Job completed successfully
- `failed`: Job failed with error
- `cancelled`: Job was cancelled

### Connectors

```python
class SourceConnector(Protocol):
    name: str
    async def read(self, source: str, batch_size: int) -> List[Record]:
        """Read a batch of records from source."""
        pass

class JSONLConnector(SourceConnector):
    pass

class ParquetConnector(SourceConnector):
    pass

class CSVConnector(SourceConnector):
    pass

class S3Connector(SourceConnector):
    pass

class HFConnector(SourceConnector):
    pass
```

### Import Job Model

```python
class ImportJob(Base):
    id = Column(UUID, primary_key=True)
    dataset_id = Column(UUID, ForeignKey("datasets.id"))
    source_type = Column(String)  # jsonl, parquet, csv, s3, hf
    source_path = Column(Text)
    status = Column(String)  # queued, running, succeeded, failed, cancelled
    progress = Column(Float)  # 0.0 to 1.0
    rows_imported = Column(BigInteger)
    total_rows = Column(BigInteger)
    checkpoint = Column(JSON)  # For resumability
    error = Column(Text)
    created_at = Column(DateTime)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
```

## Implementation Plan

### 1. Database Schema

```sql
CREATE TABLE import_jobs (
    id UUID PRIMARY KEY,
    dataset_id UUID NOT NULL REFERENCES datasets(id),
    source_type TEXT NOT NULL,
    source_path TEXT NOT NULL,
    status TEXT CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')),
    progress FLOAT DEFAULT 0.0,
    rows_imported BIGINT DEFAULT 0,
    total_rows BIGINT,
    checkpoint JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);
```

### 2. Connector Interface

```python
class SourceConnector(Protocol):
    name: str
    async def connect(self, source: str) -> None
    async def read_batch(self, batch_size: int) -> List[Record]
    async def close(self) -> None
    async def get_total_count(self) -> int
```

### 3. Import Job Worker

```python
class ImportJobWorker:
    async def run(import_job_id: str) -> None:
        # 1. Load job from DB
        # 2. Initialize connector
        # 3. Process in batches
        # 4. Update progress
        # 5. Save checkpoint
        # 6. Update job status
```

### 4. SSE Progress Stream

```python
# Valkey stream: `import:progress:{job_id}`
# Events:
# - progress: {"rows": 50000, "total": 500000}
# - completed: {"records": 500000}
# - failed: {"error": "Connection timeout"}
```

## API Endpoints

```python
POST /v1/datasets/{id}/imports
  - Start import job
  - Request: {source_type: "jsonl", source_path: "s3://bucket/file.jsonl"}
  - Response: {"job_id": "...", "status": "queued"}

GET /v1/import-jobs/{id}
  - Get job status
  - Response: {"status": "running", "progress": 0.5, ...}

GET /v1/import-jobs/{id}/events (SSE)
  - Stream progress events
  - Events: progress, completed, failed

POST /v1/import-jobs/{id}:cancel
  - Cancel job
  - Response: {"status": "cancelled"}
```

## Resumability

- Save checkpoint after each batch
- On restart, load checkpoint and resume from last position
- Checkpoint includes: connector state, rows imported, batch index

## Testing Strategy

1. Import 500k rows, verify all records in database
2. Kill worker mid-import, verify resume works
3. Import invalid format → 422 error
4. SSE stream receives progress updates

## Files to Create

```
src/api/
├── models/
│   └── import_job.py          # ImportJob model
├── core/
│   ├── connector/
│   │   ├── __init__.py
│   │   ├── base.py            # Connector protocol
│   │   ├── jsonl.py
│   │   ├── parquet.py
│   │   ├── csv.py
│   │   └── s3.py
│   └── import_worker.py
└── api/v1/endpoints/
    └── import_jobs.py
```

## Dependencies

- `pandas` or `pyarrow` for Parquet/CSV
- `boto3` or `s3fs` for S3
- `huggingface_hub` for HF
- `arq` for job queue
