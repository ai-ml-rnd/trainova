"""Ray executor for distributed curation."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class RayJob(BaseModel):
    """Ray job for distributed processing."""
    
    job_id: str
    name: str
    status: str  # "pending", "running", "completed", "failed"
    progress: float
    result_path: Optional[str] = None


class RayExecutor:
    """Ray executor for distributed curation."""
    
    def __init__(self, cluster_address: str = "ray://localhost:10001"):
        self.cluster_address = cluster_address
        self._client = None
    
    async def _get_client(self):
        """Get Ray client."""
        if self._client is None:
            import ray
            ray.init(self.cluster_address)
            self._client = ray
        return self._client
    
    async def submit_job(
        self,
        name: str,
        func: callable,
        args: List,
    ) -> RayJob:
        """Submit a job to Ray cluster."""
        client = await self._get_client()
        
        # Submit job
        job = client.submit(func, *args)
        
        return RayJob(
            job_id=job.job_id,
            name=name,
            status="running",
            progress=0.0,
        )
    
    async def get_job_status(self, job_id: str) -> RayJob:
        """Get job status."""
        client = await self._get_client()
        
        # Get job status
        job = client.get_job_status(job_id)
        
        return RayJob(
            job_id=job_id,
            status=job.status,
            progress=job.progress if hasattr(job, "progress") else 1.0,
        )
    
    async def wait_for_job(self, job_id: str) -> RayJob:
        """Wait for job completion."""
        import time
        
        while True:
            status = await self.get_job_status(job_id)
            if status.status in ["completed", "failed"]:
                return status
            time.sleep(1)
    
    async def close(self):
        """Close Ray connection."""
        if self._client:
            self._client.shutdown()
            self._client = None


# Global executor instance
ray_executor = RayExecutor()
