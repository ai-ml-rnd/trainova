"""Curation operators interface."""

from abc import ABC, abstractmethod
from typing import Protocol

import pyarrow as pa


class OpContext:
    """Operation context."""

    def __init__(self, dataset_id: str, step: str, total_rows: int = 0):
        self.dataset_id = dataset_id
        self.step = step
        self.total_rows = total_rows


class Operator(Protocol):
    """Curation operator protocol."""

    name: str
    version: str

    kind: str  # mapper, filter, dedup, tagger, stats

    def process_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.RecordBatch:
        """Process a batch of records."""
        ...


class MapperOperator(ABC):
    """Base class for mapper operators."""

    name: str
    version: str = "1.0"

    @abstractmethod
    def process_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.RecordBatch:
        """Process a batch of records."""
        ...


class FilterOperator(ABC):
    """Base class for filter operators."""

    name: str
    version: str = "1.0"

    @abstractmethod
    def filter_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.Table:
        """Filter a batch of records, return filtered table."""
        ...


class DedupOperator(ABC):
    """Base class for deduplication operators."""

    name: str
    version: str = "1.0"

    @abstractmethod
    def compute_hashes(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> list[str]:
        """Compute deduplication hashes for batch."""
        ...


class TaggerOperator(ABC):
    """Base class for tagger operators."""

    name: str
    version: str = "1.0"

    @abstractmethod
    def tag_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.RecordBatch:
        """Add tags to a batch of records."""
        ...


class StatsOperator(ABC):
    """Base class for stats operators."""

    name: str
    version: str = "1.0"

    @abstractmethod
    def compute_stats(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> dict:
        """Compute statistics for a batch of records."""
        ...


# Operator registry
OPERATOR_REGISTRY: dict[str, type[Operator]] = {}


def register_operator(cls: type[Operator]) -> type[Operator]:
    """Register an operator class."""
    OPERATOR_REGISTRY[cls.name] = cls
    return cls


def get_operator(name: str) -> type[Operator]:
    """Get an operator class by name."""
    if name not in OPERATOR_REGISTRY:
        raise ValueError(f"Operator not found: {name}")
    return OPERATOR_REGISTRY[name]


def list_operators() -> list[str]:
    """List all registered operators."""
    return list(OPERATOR_REGISTRY.keys())
