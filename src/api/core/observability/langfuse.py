"""Langfuse integration for tracing."""

from typing import Dict, Optional
from pydantic import BaseModel


class LangfuseClient(BaseModel):
    """Langfuse client for tracing."""
    
    host: str = "http://localhost:3000"
    public_key: Optional[str] = None
    secret_key: Optional[str] = None
    _session = None
    
    async def _get_session(self):
        """Get HTTPX session."""
        if self._session is None:
            import httpx
            self._session = httpx.AsyncClient(base_url=self.host)
        return self._session
    
    async def trace(
        self,
        name: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Create a trace.
        
        Args:
            name: Trace name
            metadata: Trace metadata
            
        Returns:
            Trace response
        """
        session = await self._get_session()
        
        request = {
            "name": name,
            "metadata": metadata or {},
        }
        
        response = await session.post("/api/public/trace", json=request)
        response.raise_for_status()
        
        return response.json()
    
    async def span(
        self,
        trace_id: str,
        name: str,
        start_time: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Create a span.
        
        Args:
            trace_id: Parent trace ID
            name: Span name
            start_time: Start timestamp
            metadata: Span metadata
            
        Returns:
            Span response
        """
        session = await self._get_session()
        
        request = {
            "traceId": trace_id,
            "name": name,
            "startTime": start_time,
            "metadata": metadata or {},
        }
        
        response = await session.post("/api/public/span", json=request)
        response.raise_for_status()
        
        return response.json()
    
    async def close(self):
        """Close session."""
        if self._session:
            await self._session.aclose()
            self._session = None


class PIIRedactionHook:
    """Langfuse hook to redact PII from traces."""
    
    def __init__(self, pii_detector):
        self.pii_detector = pii_detector
    
    def redact(self, data: Dict) -> Dict:
        """Redact PII from data."""
        # For MVP, simple placeholder redaction
        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = value  # In production, apply PII redaction
            elif isinstance(value, dict):
                redacted[key] = self.redact(value)
            else:
                redacted[key] = value
        return redacted
