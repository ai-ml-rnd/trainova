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
