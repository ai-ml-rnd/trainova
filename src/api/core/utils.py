"""Utility functions."""

import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


def generate_id() -> str:
    """Generate a ULID-style ID."""
    return str(uuid.uuid4())


def generate_hash(data: str) -> str:
    """Generate a SHA-256 hash."""
    return hashlib.sha256(data.encode()).hexdigest()


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def parse_timestamp(timestamp: str) -> datetime:
    """Parse ISO format timestamp."""
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def filter_none(data: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out None values from a dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def chunk_list(items: list, chunk_size: int) -> list:
    """Split a list into chunks."""
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
