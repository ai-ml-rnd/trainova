"""Annotation queue implementation."""

from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel


class QueueStrategy(str, Enum):
    """Queue assignment strategy."""
    
    ROUND_ROBIN = "round_robin"
    OVERLAP_K = "overlap_k"
    PRIORITY = "priority"


class AnnotationQueue(BaseModel):
    """Annotation queue."""
    
    id: str
    name: str
    strategy: QueueStrategy
    max_size: int = 1000
    overlap_k: int = 3


class QueueManager:
    """Manager for annotation queues."""
    
    def __init__(self):
        self._queues: Dict[str, AnnotationQueue] = {}
        self._assignment_index: Dict[str, int] = {}
    
    def create_queue(self, queue: AnnotationQueue) -> None:
        """Create an annotation queue."""
        self._queues[queue.id] = queue
        self._assignment_index[queue.id] = 0
    
    def get_queue(self, queue_id: str) -> Optional[AnnotationQueue]:
        """Get queue by ID."""
        return self._queues.get(queue_id)
    
    def assign_record(self, queue_id: str) -> int:
        """Assign a record to an annotator using queue strategy."""
        queue = self._queues.get(queue_id)
        if not queue:
            raise ValueError(f"Queue not found: {queue_id}")
        
        if queue.strategy == QueueStrategy.ROUND_ROBIN:
            idx = self._assignment_index.get(queue_id, 0)
            annotator_id = idx % 10  # 10 annotators for MVP
            self._assignment_index[queue_id] = idx + 1
            return annotator_id
        
        elif queue.strategy == QueueStrategy.OVERLAP_K:
            # Return K annotators for overlap
            return list(range(queue.overlap_k))
        
        elif queue.strategy == QueueStrategy.PRIORITY:
            # Return highest priority annotator (simplified)
            return 0
        
        else:
            raise ValueError(f"Unknown strategy: {queue.strategy}")


# Global queue manager
queue_manager = QueueManager()
