"""LiteLLM client for model access."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from app.config import settings


class LiteLLMClient:
    """Client for LiteLLM gateway."""

    def __init__(self):
        self.base_url = settings.litellm_url
        self.timeout = settings.litellm_timeout
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client (lazy init)."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    @asynccontextmanager
    async def session(self):
        """Context manager for client session."""
        client = await self._get_client()
        try:
            yield client
        finally:
            if self._client:
                await self._client.aclose()
                self._client = None

    async def create_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        virtual_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a completion."""
        client = await self._get_client()

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if response_format:
            payload["response_format"] = response_format

        headers = {"Content-Type": "application/json"}
        if virtual_key:
            headers["Authorization"] = f"Bearer {virtual_key}"

        response = await client.post("/chat/completions", json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    async def create_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        virtual_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a chat completion."""
        return await self.create_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            virtual_key=virtual_key,
        )

    async def create_embedding(
        self,
        model: str,
        input: str | List[str],
        virtual_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an embedding."""
        client = await self._get_client()

        payload = {
            "model": model,
            "input": input,
        }

        headers = {"Content-Type": "application/json"}
        if virtual_key:
            headers["Authorization"] = f"Bearer {virtual_key}"

        response = await client.post("/embeddings", json=payload, headers=headers)
        response.raise_for_status()

        return response.json()

    async def create_virtual_key(
        self,
        team_id: str,
        budgets: Optional[Dict[str, Any]] = None,
        rpm: Optional[int] = None,
        tpm: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a virtual key for a team."""
        client = await self._get_client()

        payload = {
            "team_id": team_id,
        }

        if budgets:
            payload["budgets"] = budgets

        if rpm:
            payload["rpm"] = rpm

        if tpm:
            payload["tpm"] = tpm

        response = await client.post("/key/generate", json=payload)
        response.raise_for_status()

        return response.json()

    async def revoke_virtual_key(self, key: str) -> Dict[str, Any]:
        """Revoke a virtual key."""
        client = await self._get_client()

        response = await client.post("/key/delete", json={"key": key})
        response.raise_for_status()

        return response.json()


# Global client instance
_litellm_client: Optional[LiteLLMClient] = None


def get_litellm_client() -> LiteLLMClient:
    """Get the global LiteLLM client."""
    global _litellm_client
    if _litellm_client is None:
        _litellm_client = LiteLLMClient()
    return _litellm_client
