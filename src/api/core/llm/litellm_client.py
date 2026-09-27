"""LiteLLM client for model access."""

import asyncio
from typing import List, Dict, Optional

from pydantic import BaseModel


class LiteLLMClient:
    """Client for LiteLLM gateway."""
    
    def __init__(self, base_url: str = "http://localhost:4000"):
        self.base_url = base_url
        self._session = None
    
    async def _get_session(self):
        """Get HTTPX session."""
        if self._session is None:
            import httpx
            self._session = httpx.AsyncClient(base_url=self.base_url)
        return self._session
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        response_format: Optional[Dict] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict:
        """Generate chat completion.
        
        Args:
            messages: List of message dicts with role and content
            model: Model name/route
            response_format: JSON schema for structured output
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Completion response with choices
        """
        session = await self._get_session()
        
        request = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
        }
        
        if response_format:
            request["response_format"] = response_format
        
        if max_tokens:
            request["max_tokens"] = max_tokens
        
        response = await session.post("/chat/completions", json=request)
        response.raise_for_status()
        
        return response.json()
    
    async def close(self):
        """Close session."""
        if self._session:
            await self._session.aclose()
            self._session = None


class VirtualKeyManager:
    """Manager for per-run virtual keys."""
    
    def __init__(self, admin_key: str):
        self.admin_key = admin_key
        self._session = None
        self._keys: Dict[str, str] = {}  # run_id -> virtual_key
    
    async def _get_session(self):
        """Get HTTPX session."""
        if self._session is None:
            import httpx
            self._session = httpx.AsyncClient(
                base_url="http://localhost:4000/admin",
                headers={"Authorization": f"Bearer {self.admin_key}"},
            )
        return self._session
    
    async def mint_key(self, run_id: str, budget: float = 10.0) -> str:
        """Mint a virtual key for a run.
        
        Args:
            run_id: Run identifier
            budget: USD budget for the key
            
        Returns:
            Virtual key string
        """
        session = await self._get_session()
        
        response = await session.post("/key/generate", json={
            "models": ["*"],
            "max_budget": budget,
            "duration": "1h",
        })
        response.raise_for_status()
        
        virtual_key = response.json()["key"]
        self._keys[run_id] = virtual_key
        
        return virtual_key
    
    async def get_key(self, run_id: str) -> str:
        """Get virtual key for a run."""
        if run_id not in self._keys:
            raise ValueError(f"No virtual key for run {run_id}")
        return self._keys[run_id]
    
    async def revoke_key(self, run_id: str) -> None:
        """Revoke virtual key for a run."""
        if run_id in self._keys:
            del self._keys[run_id]
            # TODO: Revoke via LiteLLM API
    
    async def close(self):
        """Close session."""
        if self._session:
            await self._session.aclose()
            self._session = None
