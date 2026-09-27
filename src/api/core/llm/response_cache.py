"""Response caching for LLM calls."""

import hashlib
from typing import Dict, Optional


class ResponseCache:
    """Cache for LLM responses."""
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
    
    def _make_key(
        self,
        messages: list,
        model: str,
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """Create cache key from request."""
        key_str = f"{model}|{temperature}|{max_tokens}|{str(messages)}"
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get(self, messages: list, model: str) -> Optional[Dict]:
        """Get cached response."""
        key = self._make_key(messages, model, 0.7, None)
        return self._cache.get(key)
    
    def set(self, messages: list, model: str, response: Dict) -> None:
        """Cache a response."""
        key = self._make_key(messages, model, 0.7, None)
        self._cache[key] = response
    
    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()


# Global cache
cache = ResponseCache()
