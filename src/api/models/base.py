"""Base models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class TimestampMixin:
    """Mixin for timestamp fields."""

    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete support."""

    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        """Mark the record as deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None


class IDMixin:
    """Mixin for UUID primary key."""

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
