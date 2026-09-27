"""Pydantic schemas for API v1."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response following RFC 9457."""

    type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None


class Pagination(BaseModel):
    """Pagination metadata."""

    page: int = 1
    page_size: int = 50
    total: Optional[int] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None


class TenantResponse(BaseModel):
    """Tenant information."""

    id: str
    slug: str
    name: str
    created_at: datetime


class ModelRouteResponse(BaseModel):
    """Model route information."""

    name: str
    model: str
    context_length: int
    max_num_seqs: int
    supports_vision: bool
    supports_guided_json: bool


class JobResponse(BaseModel):
    """Job status response."""

    id: str
    status: str
    progress: float
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None


class ExportResponse(BaseModel):
    """Export response."""

    id: str
    format: str
    status: str
    download_url: Optional[str] = None


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


class FieldDefResponse(BaseModel):
    """Field definition response."""

    id: str
    name: str
    type: str = Field(..., pattern="^(text|markdown|chat|image|image_list|json|custom)$")
    required: bool
    created_at: datetime


class QuestionDefResponse(BaseModel):
    """Question definition response."""

    id: str
    name: str
    type: str = Field(
        ...,
        pattern="^(label|multi_label|span|text|rating|rubric|ranking|pairwise|kto|chat_edit|bbox|polygon|keypoints|vqa|caption)$",
    )
    settings: dict
    required: bool
    created_at: datetime


class DatasetSchemaResponse(BaseModel):
    """Dataset schema response."""

    id: str
    field_defs: List[FieldDefResponse]
    question_defs: List[QuestionDefResponse]
    created_at: datetime


class DatasetResponse(BaseModel):
    """Dataset response."""

    id: str
    name: str
    kind: str = Field(..., pattern="^(pretrain|sft|preference|vlm|eval|generic)$")
    schema_id: Optional[str] = None
    lance_uri: Optional[str] = None
    draft_lance_version: Optional[int] = None
    created_at: datetime
    created_by: str


class DatasetListResponse(BaseModel):
    """Dataset list response with pagination."""

    datasets: List[DatasetResponse]
    pagination: Pagination


class DatasetCreate(BaseModel):
    """Create dataset request."""

    name: str = Field(..., min_length=1, max_length=100)
    kind: str = Field(..., pattern="^(pretrain|sft|preference|vlm|eval|generic)$")
    workspace_id: str
    schema: Optional[dict] = Field(default=None)


class DatasetUpdate(BaseModel):
    """Update dataset request."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    kind: Optional[str] = Field(default=None, pattern="^(pretrain|sft|preference|vlm|eval|generic)$")
    schema: Optional[dict] = Field(default=None)


class RecordCreate(BaseModel):
    """Record creation request."""

    record_id: str
    fields: dict
    metadata: Optional[dict] = None
    provenance: Optional[List[dict]] = None
    quality: Optional[dict] = None
    status: Optional[str] = None
    reject_reason: Optional[str] = None
    embedding: Optional[List[float]] = None


class RecordResponse(BaseModel):
    """Record response."""

    record_id: str
    fields: dict
    metadata: dict
    provenance: List[dict]
    quality: dict
    status: str
    reject_reason: Optional[str] = None
    embedding: Optional[List[float]] = None


class BulkRecordResponse(BaseModel):
    """Bulk record response."""

    added: int


class FilterRequest(BaseModel):
    """Filter request with DSL."""

    filter: dict
    limit: int = 100


class SemanticSearchRequest(BaseModel):
    """Semantic search request."""

    vector: List[float]
    k: int = 10


class ImportJobCreate(BaseModel):
    """Import job creation request."""

    dataset_id: str
    source_type: str = Field(..., pattern="^(jsonl|parquet|csv|s3|hf)$")
    source_path: str


class ImportJobResponse(BaseModel):
    """Import job response."""

    id: str
    dataset_id: str
    source_type: str
    source_path: str
    status: str
    progress: float
    rows_imported: Optional[int] = None
    total_rows: Optional[int] = None
    error: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class OperatorKind(StrEnum):
    """Operator kind enum."""

    MAPPER = "mapper"
    FILTER = "filter"
    DEDUP = "dedup"
    TAGGER = "tagger"
    STATS = "stats"


class OperatorResponse(BaseModel):
    """Operator response."""

    name: str
    version: str
    kind: str


class CurationRecipeCreate(BaseModel):
    """Curation recipe creation request."""

    name: str
    version: str
    operators: List[dict]


class CurationRecipeResponse(BaseModel):
    """Curation recipe response."""

    id: str
    name: str
    version: str
    operators: List[dict]


class CurationRunCreate(BaseModel):
    """Curation run creation request."""

    dataset_id: str
    input_version: Optional[int] = None


class CurationRunResponse(BaseModel):
    """Curation run response."""

    id: str
    recipe_id: str
    dataset_id: str
    status: str
    input_version: Optional[int] = None
    stage_stats: List[dict]
    created_at: str
