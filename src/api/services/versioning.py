"""Dataset versioning service."""

import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.config import settings


class DatasetVersion(BaseModel):
    """Dataset version."""

    id: str
    dataset_id: str
    lance_version: int
    parent_ids: List[str]
    tag: Optional[str] = None
    message: Optional[str] = None
    manifest_sha256: str
    stats: Dict[str, Any]
    created_by: str
    created_at: datetime


class VersioningService:
    """Service for dataset versioning."""

    def __init__(self):
        self.versions: Dict[str, DatasetVersion] = {}

    async def commit_version(
        self,
        dataset_id: str,
        lance_version: int,
        parent_ids: List[str],
        manifest_data: Dict[str, Any],
        stats: Dict[str, Any],
        created_by: str,
        tag: Optional[str] = None,
        message: Optional[str] = None,
    ) -> DatasetVersion:
        """Commit a new version."""
        version_id = str(uuid.uuid4())

        # Compute manifest hash
        manifest_json = str(manifest_data)
        manifest_hash = hashlib.sha256(manifest_json.encode()).hexdigest()

        version = DatasetVersion(
            id=version_id,
            dataset_id=dataset_id,
            lance_version=lance_version,
            parent_ids=parent_ids,
            tag=tag,
            message=message,
            manifest_sha256=manifest_hash,
            stats=stats,
            created_by=created_by,
            created_at=datetime.utcnow(),
        )

        self.versions[version_id] = version
        return version

    async def get_version(
        self,
        version_id: str,
    ) -> Optional[DatasetVersion]:
        """Get a version by ID."""
        return self.versions.get(version_id)

    async def get_versions_for_dataset(
        self,
        dataset_id: str,
    ) -> List[DatasetVersion]:
        """Get all versions for a dataset."""
        return [
            v for v in self.versions.values()
            if v.dataset_id == dataset_id
        ]

    async def diff_versions(
        self,
        version_a_id: str,
        version_b_id: str,
    ) -> Dict[str, Any]:
        """Get diff between two versions."""
        version_a = self.versions.get(version_a_id)
        version_b = self.versions.get(version_b_id)

        if not version_a or not version_b:
            raise ValueError("Version not found")

        return {
            "version_a": version_a.id,
            "version_b": version_b.id,
            "changes": {
                "records_added": 0,
                "records_removed": 0,
                "records_modified": 0,
            },
        }

    async def branch_version(
        self,
        version_id: str,
        branch_name: str,
    ) -> DatasetVersion:
        """Create a branch from a version."""
        version = self.versions.get(version_id)
        if not version:
            raise ValueError(f"Version not found: {version_id}")

        branch_id = str(uuid.uuid4())
        branch_version = DatasetVersion(
            id=branch_id,
            dataset_id=version.dataset_id,
            lance_version=version.lance_version,
            parent_ids=[version_id],
            tag=branch_name,
            message=f"Branch from {version_id}",
            manifest_sha256=version.manifest_sha256,
            stats=version.stats,
            created_by=version.created_by,
            created_at=datetime.utcnow(),
        )

        self.versions[branch_id] = branch_version
        return branch_version


# Global instance
_versioning_service: Optional[VersioningService] = None


def get_versioning_service() -> VersioningService:
    """Get the global versioning service."""
    global _versioning_service
    if _versioning_service is None:
        _versioning_service = VersioningService()
    return _versioning_service
