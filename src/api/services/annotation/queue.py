"""Annotation queue service."""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.config import settings


class AnnotationQueue(BaseModel):
    """Annotation queue."""

    id: str
    name: str
    dataset_id: str
    strategy: str  # round_robin, overlap_k, active_learning, stratified
    created_at: datetime


class Assignment(BaseModel):
    """Annotation assignment."""

    id: str
    queue_id: str
    record_id: str
    user_id: str
    status: str  # leased, completed, discarded
    expires_at: datetime
    created_at: datetime


class AnnotationQueueService:
    """Service for managing annotation queues."""

    def __init__(self):
        self.queues: Dict[str, AnnotationQueue] = {}
        self.assignments: Dict[str, Assignment] = {}
        self.lease_ttl = timedelta(minutes=30)

    async def create_queue(
        self,
        name: str,
        dataset_id: str,
        strategy: str,
        user_id: str,
    ) -> AnnotationQueue:
        """Create a new annotation queue."""
        queue_id = str(uuid.uuid4())
        queue = AnnotationQueue(
            id=queue_id,
            name=name,
            dataset_id=dataset_id,
            strategy=strategy,
            created_at=datetime.utcnow(),
        )
        self.queues[queue_id] = queue
        return queue

    async def lease_next(
        self,
        queue_id: str,
        user_id: str,
        k: int = 1,
    ) -> List[str]:
        """Lease the next record(s) for annotation."""
        if queue_id not in self.queues:
            raise ValueError(f"Queue not found: {queue_id}")

        # TODO: Implement lease logic with SELECT ... FOR UPDATE SKIP LOCKED
        # For now, return placeholder record IDs
        record_ids = []
        for i in range(k):
            record_ids.append(f"record-{uuid.uuid4().hex[:8]}")
            self.assignments[record_ids[-1]] = Assignment(
                id=record_ids[-1],
                queue_id=queue_id,
                record_id=record_ids[-1],
                user_id=user_id,
                status="leased",
                expires_at=datetime.utcnow() + self.lease_ttl,
                created_at=datetime.utcnow(),
            )

        return record_ids

    async def get_next_for_user(
        self,
        queue_id: str,
        user_id: str,
    ) -> Optional[str]:
        """Get next record for a specific user (round-robin)."""
        if queue_id not in self.queues:
            raise ValueError(f"Queue not found: {queue_id}")

        # TODO: Implement round-robin logic
        return f"record-{uuid.uuid4().hex[:8]}"

    async def complete_assignment(
        self,
        assignment_id: str,
        response: Dict[str, Any],
    ) -> bool:
        """Complete an assignment with a response."""
        if assignment_id not in self.assignments:
            return False

        assignment = self.assignments[assignment_id]
        assignment.status = "completed"
        # Store response in database
        return True

    async def get_assignments_for_user(
        self,
        queue_id: str,
        user_id: str,
    ) -> List[Assignment]:
        """Get all assignments for a user in a queue."""
        return [
            a for a in self.assignments.values()
            if a.queue_id == queue_id and a.user_id == user_id
        ]

    async def refresh_lease(
        self,
        assignment_id: str,
    ) -> bool:
        """Refresh an assignment lease."""
        if assignment_id not in self.assignments:
            return False

        assignment = self.assignments[assignment_id]
        assignment.expires_at = datetime.utcnow() + self.lease_ttl
        return True

    async def expire_leases(self) -> List[str]:
        """Expire all expired leases."""
        now = datetime.utcnow()
        expired = []

        for assignment_id, assignment in list(self.assignments.items()):
            if assignment.expires_at < now and assignment.status == "leased":
                assignment.status = "expired"
                expired.append(assignment_id)

        return expired


# Global instance
_annotation_queue_service: Optional[AnnotationQueueService] = None


def get_annotation_queue_service() -> AnnotationQueueService:
    """Get the global annotation queue service."""
    global _annotation_queue_service
    if _annotation_queue_service is None:
        _annotation_queue_service = AnnotationQueueService()
    return _annotation_queue_service
