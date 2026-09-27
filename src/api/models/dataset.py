"""Dataset models for SQLAlchemy."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UUID,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import BIGINT, JSONB
from sqlalchemy.orm import relationship

from app.dependencies import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(100))
    role = Column(String(50))  # owner, admin, curator, lead, annotator, viewer, auditor
    created_at = Column(DateTime, default=datetime.utcnow)

    datasets = relationship("Dataset", backref="created_by_user")
    dataset_versions = relationship("DatasetVersion", backref="created_by_user")


class Tenant(Base):
    """Tenant model."""

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    litellm_team_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    workspaces = relationship("Workspace", back_populates="tenant")


class Workspace(Base):
    """Workspace model."""

    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False)

    tenant = relationship("Tenant", back_populates="workspaces")
    datasets = relationship("Dataset", back_populates="workspace")


class Dataset(Base):
    """Dataset model."""

    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(100), nullable=False)
    kind = Column(
        Enum("pretrain", "sft", "preference", "vlm", "eval", "generic", name="dataset_kind"),
        nullable=False,
    )
    schema_id = Column(UUID(as_uuid=True), ForeignKey("dataset_schemas.id"))
    lance_uri = Column(Text)
    draft_lance_version = Column(BIGINT)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="datasets")
    schema = relationship("DatasetSchema", back_populates="datasets")
    versions = relationship("DatasetVersion", back_populates="dataset")


class DatasetSchema(Base):
    """Dataset schema model."""

    __tablename__ = "dataset_schemas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    datasets = relationship("Dataset", back_populates="schema")
    field_defs = relationship("FieldDef", back_populates="schema", cascade="all, delete-orphan")
    question_defs = relationship("QuestionDef", back_populates="schema", cascade="all, delete-orphan")


class FieldDef(Base):
    """Field definition model."""

    __tablename__ = "field_defs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schema_id = Column(UUID(as_uuid=True), ForeignKey("dataset_schemas.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(
        Enum("text", "markdown", "chat", "image", "image_list", "json", "custom", name="field_type"),
        nullable=False,
    )
    required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    schema = relationship("DatasetSchema", back_populates="field_defs")


class QuestionDef(Base):
    """Question definition model."""

    __tablename__ = "question_defs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schema_id = Column(UUID(as_uuid=True), ForeignKey("dataset_schemas.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(
        Enum(
            "label", "multi_label", "span", "text", "rating", "rubric", "ranking",
            "pairwise", "kto", "chat_edit", "bbox", "polygon", "keypoints", "vqa", "caption",
            name="question_type",
        ),
        nullable=False,
    )
    settings = Column(JSON, default=dict)
    required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    schema = relationship("DatasetSchema", back_populates="question_defs")


class DatasetVersion(Base):
    """Dataset version model."""

    __tablename__ = "dataset_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    lance_version = Column(BIGINT, nullable=False)
    parent_ids = Column(JSON, default=list)
    tag = Column(String(100))
    message = Column(Text)
    run_id = Column(UUID(as_uuid=True))
    manifest_sha256 = Column(String(64))
    stats = Column(JSON, default=dict)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="versions")


class Record(Base):
    """Record model for storing dataset records."""

    __tablename__ = "records"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    record_id = Column(Text, nullable=False)
    fields = Column(JSONB, nullable=False)
    metadata = Column(JSONB, default=dict)
    provenance = Column(JSONB, default=list)
    quality = Column(JSONB, default=dict)
    status = Column(
        Enum("pending", "accepted", "rejected", "needs_review", name="record_status"),
        default="pending",
    )
    reject_reason = Column(Text)
    embedding = Column(JSONB)  # Will store as vector in pgvector for MVP
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", backref="records")

    __table_args__ = (
        Index("idx_records_dataset_id", "dataset_id"),
        Index("idx_records_record_id", "record_id"),
        Index("idx_records_status", "status"),
        Index("idx_records_quality_lang", "quality", postgresql_using="gin"),
    )
