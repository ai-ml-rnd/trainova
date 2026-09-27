"""Dataset branches and merges."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class Branch(BaseModel):
    """Dataset branch."""
    
    name: str
    parent_id: Optional[str] = None
    parent_version: Optional[int] = None
    tip_version: int
    created_at: str


class MergeRequest(BaseModel):
    """Merge request."""
    
    id: str
    source_branch: str
    target_branch: str
    status: str  # "open", "merged", "rejected"
    conflicts: List[Dict] = []


class BranchManager:
    """Manager for dataset branches."""
    
    def __init__(self):
        self._branches: Dict[str, Branch] = {}
        self._merge_requests: Dict[str, MergeRequest] = {}
    
    async def create_branch(
        self,
        dataset_id: str,
        branch_name: str,
        parent_version: int,
    ) -> Branch:
        """Create a new branch."""
        branch = Branch(
            name=branch_name,
            parent_id=dataset_id,
            parent_version=parent_version,
            tip_version=parent_version + 1,
            created_at="2026-09-27T00:00:00Z",
        )
        
        self._branches[branch_name] = branch
        return branch
    
    async def get_branch(self, branch_name: str) -> Optional[Branch]:
        """Get branch by name."""
        return self._branches.get(branch_name)
    
    async def merge(
        self,
        source_branch: str,
        target_branch: str,
    ) -> MergeRequest:
        """Create a merge request."""
        merge = MergeRequest(
            id=f"mr-{source_branch}-{target_branch}",
            source_branch=source_branch,
            target_branch=target_branch,
            status="open",
        )
        
        self._merge_requests[merge.id] = merge
        return merge
    
    async def get_merge_request(self, mr_id: str) -> Optional[MergeRequest]:
        """Get merge request by ID."""
        return self._merge_requests.get(mr_id)
    
    async def get_branch_diff(
        self,
        branch1: str,
        branch2: str,
    ) -> List[Dict]:
        """Get row-level diff between branches."""
        # For MVP, return placeholder diff
        return [
            {"row_id": "123", "type": "modified", "before": "old", "after": "new"},
            {"row_id": "456", "type": "added", "before": None, "after": "new"},
        ]
