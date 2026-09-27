"""Lease management for annotation tasks."""

import asyncio
import time
from typing import Dict, Optional
from pydantic import BaseModel


class Lease(BaseModel):
    """Lease for annotation task."""
    
    task_id: str
    annotator_id: str
    created_at: float
    expires_at: float
    ttl: int


class LeaseManager:
    """Manager for annotation task leases."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._leases: Dict[str, Lease] = {}
        self._default_ttl = default_ttl
    
    def acquire(self, task_id: str, annotator_id: str, ttl: Optional[int] = None) -> Optional[Lease]:
        """Acquire a lease for a task.
        
        Returns lease if successful, None if already leased.
        """
        if task_id in self._leases:
            # Check if lease is expired
            lease = self._leases[task_id]
            if time.time() < lease.expires_at:
                return None  # Lease still valid
        
        ttl = ttl or self._default_ttl
        lease = Lease(
            task_id=task_id,
            annotator_id=annotator_id,
            created_at=time.time(),
            expires_at=time.time() + ttl,
            ttl=ttl,
        )
        self._leases[task_id] = lease
        return lease
    
    def release(self, task_id: str) -> bool:
        """Release a lease."""
        if task_id in self._leases:
            del self._leases[task_id]
            return True
        return False
    
    def extend(self, task_id: str, ttl: int) -> bool:
        """Extend a lease."""
        if task_id in self._leases:
            lease = self._leases[task_id]
            lease.expires_at = time.time() + ttl
            lease.ttl = ttl
            return True
        return False
    
    def get_expired(self) -> List[str]:
        """Get expired lease task IDs."""
        now = time.time()
        return [
            task_id for task_id, lease in self._leases.items()
            if now >= lease.expires_at
        ]
    
    def get_active(self) -> Dict[str, Lease]:
        """Get active (non-expired) leases."""
        now = time.time()
        return {
            task_id: lease for task_id, lease in self._leases.items()
            if now < lease.expires_at
        }


# Global lease manager
lease_manager = LeaseManager()
