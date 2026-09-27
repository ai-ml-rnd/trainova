"""Base connector interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from core.record_store import Record


class SourceConnector(ABC):
    """Base class for data source connectors."""
    
    name: str = "base"
    
    @abstractmethod
    async def connect(self, source: str) -> None:
        """Connect to the data source.
        
        Args:
            source: Source path/URL
        """
        pass
    
    @abstractmethod
    async def read_batch(self, batch_size: int) -> List[Record]:
        """Read a batch of records from source.
        
        Args:
            batch_size: Number of records to read
            
        Returns:
            List of records
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the connection."""
        pass
    
    @abstractmethod
    async def get_total_count(self) -> int:
        """Get total count of records in source."""
        pass
    
    @abstractmethod
    def get_checkpoint(self) -> dict:
        """Get current checkpoint state for resumability."""
        return {}
    
    @abstractmethod
    def restore_from_checkpoint(self, checkpoint: dict) -> None:
        """Restore connector state from checkpoint."""
        pass
