"""Operator interface and base classes."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol, Literal, Optional
from dataclasses import dataclass

import pyarrow as pa


class OperatorKind(str, Enum):
    """Operator kind enum."""

    MAPPER = "mapper"
    FILTER = "filter"
    DEDUP = "dedup"
    TAGGER = "tagger"
    STATS = "stats"


@dataclass
class OpContext:
    """Context for operator execution."""
    
    dataset_id: str
    stage: str
    checkpoint: Optional[dict] = None


class Operator(Protocol):
    """Operator interface for curation pipeline."""
    
    name: str
    version: str
    kind: OperatorKind
    
    @abstractmethod
    def process_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.RecordBatch:
        """Process a batch, return transformed batch."""
        pass


class MapperOperator(ABC):
    """Base class for mapper operators (adds/modifies columns)."""
    
    name: str = "base_mapper"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.MAPPER
    
    @abstractmethod
    def map(self, batch: pa.RecordBatch) -> pa.RecordBatch:
        """Map batch to transformed batch."""
        pass
    
    def process_batch(self, batch: pa.RecordBatch, ctx: OpContext) -> pa.RecordBatch:
        """Process batch (default implementation)."""
        return self.map(batch)


class FilterOperator(ABC):
    """Base class for filter operators (removes rows)."""
    
    name: str = "base_filter"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.FILTER
    
    @abstractmethod
    def filter(self, batch: pa.RecordBatch) -> pa.RecordBatch:
        """Filter batch, return rows to keep."""
        pass
    
    def process_batch(self, batch: pa.RecordBatch, ctx: OpContext) -> pa.RecordBatch:
        """Process batch (default implementation)."""
        return self.filter(batch)


class DedupOperator(ABC):
    """Base class for deduplication operators."""
    
    name: str = "base_dedup"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.DEDUP
    
    @abstractmethod
    def identify_duplicates(self, batch: pa.RecordBatch) -> list:
        """Identify duplicate rows."""
        pass
    
    def process_batch(self, batch: pa.RecordBatch, ctx: OpContext) -> pa.RecordBatch:
        """Process batch (default implementation)."""
        dup_ids = self.identify_duplicates(batch)
        # Keep non-duplicates
        mask = [i not in dup_ids for i in range(len(batch))]
        return batch.filter(mask)


class TaggerOperator(ABC):
    """Base class for tagger operators (adds tags)."""
    
    name: str = "base_tagger"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.TAGGER
    
    @abstractmethod
    def tag(self, batch: pa.RecordBatch) -> dict:
        """Tag batch, return tag dict."""
        pass
    
    def process_batch(self, batch: pa.RecordBatch, ctx: OpContext) -> pa.RecordBatch:
        """Process batch (default implementation)."""
        tags = self.tag(batch)
        # Add tags as columns
        for key, values in tags.items():
            batch = batch.append_column(key, pa.array(values))
        return batch
