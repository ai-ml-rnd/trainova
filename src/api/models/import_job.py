"""Import job models for SQLAlchemy."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UUID,
    JSON,
)
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.orm import relationship

from app.dependencies import Base


class ImportJobStatus(str, Enum):
    """Import job status enum."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SourceType(str, Enum):
    """Source type enum."""

    JSONL = "jsonl"
    PARQUET = "parquet"
    CSV = "csv"
    S3 = "s3"
    HF = "hf"


class ImportJob(Base):
    """Import job model."""

    __tablename__ = "import_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    source_path = Column(Text, nullable=False)
    status = Column(Enum(ImportJobStatus), default=ImportJobStatus.QUEUED)
    progress = Column(Float, default=0.0)
    rows_imported = Column(BIGINT, default=0)
    total_rows = Column(BIGINT)
    checkpoint = Column(JSON, default=dict)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    dataset = relationship("Dataset", backref="import_jobs")
