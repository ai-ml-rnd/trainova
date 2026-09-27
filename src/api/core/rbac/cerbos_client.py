"""Cerbos client for RBAC."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class Resource(BaseModel):
    """Resource with RBAC."""
    
    id: str
    type: str
    owner: str
    sensitivity: str  # public, internal, restricted
    policy: Dict


class CerbosClient:
    """Cerbos client for RBAC."""
    
    def __init__(self, host: str = "http://localhost:3592"):
        self.host = host
        self._session = None
    
    async def _get_session(self):
        """Get HTTPX session."""
        if self._session is None:
            import httpx
            self._session = httpx.AsyncClient(base_url=self.host)
        return self._session
    
    async def check(
        self,
        principal: str,
        resource: Resource,
        actions: List[str],
    ) -> bool:
        """Check if principal can perform actions on resource."""
        session = await self._get_session()
        
        request = {
            "principal": {"id": principal},
            "resource": {
                "kind": resource.type,
                "id": resource.id,
                "attr": {
                    "owner": resource.owner,
                    "sensitivity": resource.sensitivity,
                },
            },
            "action": actions[0],
        }
        
        response = await session.post("/api/check", json=request)
        response.raise_for_status()
        
        result = response.json()
        return result.get("allowed", False)
    
    async def close(self):
        """Close session."""
        if self._session:
            await self._session.aclose()
            self._session = None


# Global client instance
cerbos_client = CerbosClient()
