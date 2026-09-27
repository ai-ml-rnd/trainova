"""Record store interface and implementations."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class QualityMetrics(BaseModel):
    """Quality metrics for a record."""
    
    lang: Optional[str] = None
    lang_score: Optional[float] = None
    quality_score: Optional[float] = None
    pii_flags: List[str] = []
    dup_cluster_id: Optional[str] = None


class ProvenanceEntry(BaseModel):
    """Provenance entry for a record."""
    
    op: str
    op_version: str
    run_id: str
    model_route: Optional[str] = None
    at: datetime


class Record(BaseModel):
    """Record model for dataset records."""
    
    record_id: str
    fields: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    provenance: List[ProvenanceEntry] = []
    quality: QualityMetrics = QualityMetrics()
    status: str = "pending"
    reject_reason: Optional[str] = None
    embedding: Optional[List[float]] = None


class ScanResult(BaseModel):
    """Result of a scan operation."""
    
    records: List[Record]
    next_cursor: Optional[str] = None


class RecordStore(ABC):
    """Abstract record store interface."""
    
    @abstractmethod
    async def bulk_add(self, dataset_id: str, records: List[Record]) -> int:
        """Add multiple records to a dataset.
        
        Args:
            dataset_id: The dataset ID
            records: List of records to add
            
        Returns:
            Number of records added
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, dataset_id: str, record_id: str) -> Optional[Record]:
        """Get a record by its ID.
        
        Args:
            dataset_id: The dataset ID
            record_id: The record ID
            
        Returns:
            Record if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def scan(
        self,
        dataset_id: str,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> ScanResult:
        """Scan records in a dataset.
        
        Args:
            dataset_id: The dataset ID
            cursor: Cursor for pagination (optional)
            limit: Maximum number of records to return
            
        Returns:
            ScanResult with records and next cursor
        """
        pass
    
    @abstractmethod
    async def filter(
        self,
        dataset_id: str,
        filter_expr: Dict[str, Any],
        limit: int = 100
    ) -> List[Record]:
        """Filter records in a dataset.
        
        Args:
            dataset_id: The dataset ID
            filter_expr: Filter expression (DSL)
            limit: Maximum number of records to return
            
        Returns:
            List of matching records
        """
        pass
    
    @abstractmethod
    async def semantic_search(
        self,
        dataset_id: str,
        vector: List[float],
        k: int = 10
    ) -> List[Record]:
        """Semantic search for similar records.
        
        Args:
            dataset_id: The dataset ID
            vector: Query vector
            k: Number of nearest neighbors to return
            
        Returns:
            List of nearest neighbor records
        """
        pass
