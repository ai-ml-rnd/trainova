# Phase 1 M1.2 Lance Record Store Implementation Plan

## Overview

Implement record store interface with LanceDB backend for storing and querying records.

## Requirements

From tasks.md:
- Bulk add (≤10k records), get by ID, cursor scan
- Filter DSL (no raw SQL)
- Vector search with pgvector for MVP
- 1M-record dataset next-page p95 < 200 ms

## Architecture

### Record Store Interface

```python
class RecordStore:
    async def bulk_add(dataset_id: str, records: List[Record]) -> int
    async def get_by_id(dataset_id: str, record_id: str) -> Optional[Record]
    async def scan(dataset_id: str, cursor: Optional[str] = None, limit: int = 100) -> ScanResult
    async def filter(dataset_id: str, filter_expr: FilterExpr, limit: int = 100) -> List[Record]
    async def semantic_search(dataset_id: str, vector: List[float], k: int = 10) -> List[Record]
```

### Filter DSL

```python
# Examples:
# {"field": "lang", "op": "==", "value": "en"}
# {"field": "quality_score", "op": ">", "value": 0.5}
# {"field": "tags", "op": "contains", "value": "news"}
# {"field": "embedding", "op": "nearest", "vector": [...], "k": 10}
```

### Record Schema

```python
class Record:
    record_id: str  # ULID
    fields: dict  # Per dataset schema
    metadata: dict
    provenance: List[ProvenanceEntry]
    quality: QualityMetrics
    status: str  # pending/accepted/rejected/needs_review
    reject_reason: Optional[str]
    embedding: Optional[List[float]]  # For vector search
```

## Implementation Plan

### 1. Database Schema (PostgreSQL)

```sql
CREATE TABLE records (
    id UUID PRIMARY KEY,
    dataset_id UUID NOT NULL REFERENCES datasets(id),
    record_id TEXT NOT NULL,
    fields JSONB NOT NULL,
    metadata JSONB,
    provenance JSONB,
    quality JSONB,
    status TEXT CHECK (status IN ('pending', 'accepted', 'rejected', 'needs_review')),
    reject_reason TEXT,
    embedding VECTOR(768),  -- pgvector
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_records_dataset_id ON records(dataset_id);
CREATE INDEX idx_records_record_id ON records(record_id);
CREATE INDEX idx_records_status ON records(status);
CREATE INDEX idx_records_quality_lang ON records((quality->>'lang'));
CREATE INDEX idx_records_embedding ON records USING ivfflat (embedding vector_cosine_ops);
```

### 2. Lance Integration

For MVP: Use pgvector + PostgreSQL
For scale: Use LanceDB with S3 backend

```python
# For MVP, we'll use pgvector
# For production scale, switch to LanceDB

import lancedb
from lancedb.pydantic import LanceModel, Vector

class RecordLanceModel(LanceModel):
    record_id: str
    fields: dict
    metadata: dict
    embedding: Vector(768)
```

### 3. RecordStore Implementation

```python
class PostgresRecordStore(RecordStore):
    async def bulk_add(dataset_id: str, records: List[Record]) -> int
    async def get_by_id(dataset_id: str, record_id: str) -> Optional[Record]
    async def scan(dataset_id: str, cursor: Optional[str] = None, limit: int = 100) -> ScanResult
    async def filter(dataset_id: str, filter_expr: FilterExpr, limit: int = 100) -> List[Record]
    async def semantic_search(dataset_id: str, vector: List[float], k: int = 10) -> List[Record]
```

### 4. Filter DSL Parser

```python
def parse_filter(filter_expr: dict) -> Tuple[Column, Any, str]:
    """Parse filter expression into SQLAlchemy clause."""
    field = filter_expr["field"]
    op = filter_expr["op"]
    value = filter_expr["value"]
    
    column = get_sql_column(field)
    
    if op == "==":
        return column == value
    elif op == "!=":
        return column != value
    elif op == ">":
        return column > value
    elif op == "<":
        return column < value
    elif op == ">=":
        return column >= value
    elif op == "<=":
        return column <= value
    elif op == "contains":
        return column.contains(value)
    elif op == "in":
        return column.in_(value)
    else:
        raise ValueError(f"Unknown operator: {op}")
```

### 5. API Endpoints

```python
POST /v1/datasets/{id}/records:bulk
  - Add ≤10k records
  - Returns: {"added": int}

GET /v1/datasets/{id}/records/{record_id}
  - Get single record

GET /v1/datasets/{id}/records
  - Scan with cursor pagination
  - Query params: cursor, limit

POST /v1/datasets/{id}/records:search
  - Filter with DSL
  - Body: {"filter": {...}, "limit": 100, "cursor": "..."}
```

## Testing Strategy

1. Unit tests for RecordStore interface
2. Integration tests with test database
3. Performance tests: 1M records, p95 < 200 ms
4. DSL fuzz tests: 1000 random filters, verify no SQL injection

## Migration Steps

1. Create database migration for records table
2. Implement RecordStore with pgvector
3. Add API endpoints
4. Add tests
5. Performance testing

## Future Enhancements

1. Switch to LanceDB for S3-backed storage
2. Add vector index (IVFFlat, HNSW)
3. Implement resumable imports
4. Add record versioning
