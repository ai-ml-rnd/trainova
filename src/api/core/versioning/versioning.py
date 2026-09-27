"""Dataset versioning."""

from typing import Dict, List, Optional
from pydantic import BaseModel
import time


class DatasetVersion(BaseModel):
    """Dataset version."""
    
    id: str
    dataset_id: str
    version: int
    commit_hash: str
    manifest_path: str
    row_count: int
    created_at: float
    tags: List[str] = []
    is_draft: bool = True


class VersionManager:
    """Manager for dataset versions."""
    
    def __init__(self):
        self._versions: Dict[str, List[DatasetVersion]] = {}
        self._drafts: Dict[str, DatasetVersion] = {}
    
    def create_draft(self, dataset_id: str) -> DatasetVersion:
        """Create a draft version."""
        version = DatasetVersion(
            id=f"{dataset_id}-draft",
            dataset_id=dataset_id,
            version=0,
            commit_hash="",
            manifest_path="",
            row_count=0,
            created_at=time.time(),
            is_draft=True,
        )
        self._drafts[dataset_id] = version
        return version
    
    def commit_version(
        self,
        dataset_id: str,
        commit_hash: str,
        manifest_path: str,
        row_count: int,
        tags: Optional[List[str]] = None,
    ) -> DatasetVersion:
        """Commit a draft to a version."""
        draft = self._drafts.get(dataset_id)
        if not draft:
            raise ValueError(f"No draft for dataset {dataset_id}")
        
        # Get next version number
        versions = self._versions.get(dataset_id, [])
        next_version = len(versions) + 1
        
        version = DatasetVersion(
            id=f"{dataset_id}-v{next_version}",
            dataset_id=dataset_id,
            version=next_version,
            commit_hash=commit_hash,
            manifest_path=manifest_path,
            row_count=row_count,
            created_at=time.time(),
            tags=tags or [],
            is_draft=False,
        )
        
        if dataset_id not in self._versions:
            self._versions[dataset_id] = []
        self._versions[dataset_id].append(version)
        
        del self._drafts[dataset_id]
        
        return version
    
    def get_version(self, dataset_id: str, version: int) -> Optional[DatasetVersion]:
        """Get a specific version."""
        versions = self._versions.get(dataset_id, [])
        for v in versions:
            if v.version == version:
                return v
        return None
    
    def get_latest_version(self, dataset_id: str) -> Optional[DatasetVersion]:
        """Get latest version."""
        versions = self._versions.get(dataset_id, [])
        if not versions:
            return None
        return versions[-1]
    
    def tag_version(self, dataset_id: str, version: int, tag: str) -> bool:
        """Add a tag to a version."""
        versions = self._versions.get(dataset_id, [])
        for v in versions:
            if v.version == version:
                v.tags.append(tag)
                return True
        return False
    
    def list_versions(self, dataset_id: str) -> List[DatasetVersion]:
        """List all versions for a dataset."""
        return self._versions.get(dataset_id, [])


# Global version manager
version_manager = VersionManager()
