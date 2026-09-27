"""Offline vLLM on Ray for > 1M rows."""

from typing import List, Dict
from pydantic import BaseModel


class OfflineJob(BaseModel):
    """Offline vLLM job."""
    
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    rows_processed: int
    cost: float


class OfflineVLLM:
    """Offline vLLM on Ray."""
    
    def __init__(self):
        self._jobs: Dict[str, OfflineJob] = {}
    
    async def run_job(
        self,
        prompts: List[str],
        model: str = "gen-default",
    ) -> OfflineJob:
        """Run offline vLLM job."""
        import time
        
        job_id = f"job-{int(time.time())}"
        
        job = OfflineJob(
            job_id=job_id,
            status="pending",
            rows_processed=0,
            cost=0.0,
        )
        
        # Simulate job execution
        import asyncio
        await asyncio.sleep(1)
        
        job.status = "running"
        job.rows_processed = len(prompts)
        job.cost = len(prompts) * 0.001  # Placeholder cost
        
        await asyncio.sleep(1)
        job.status = "completed"
        
        self._jobs[job_id] = job
        return job
    
    def get_job(self, job_id: str) -> OfflineJob:
        """Get job status."""
        return self._jobs.get(job_id)


async def offline_vllm(prompts: List[str]) -> Dict:
    """Run offline vLLM job.
    
    Expected: > 1M rows with cost accounting
    """
    vllm = OfflineVLLM()
    job = await vllm.run_job(prompts)
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "rows_processed": job.rows_processed,
        "cost": job.cost,
    }
