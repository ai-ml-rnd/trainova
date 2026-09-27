"""Route semaphores for rate limiting."""

import asyncio
from typing import Dict, Optional


class RouteSemaphore:
    """Semaphore per route for rate limiting."""
    
    def __init__(self):
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
    
    def get_semaphore(self, route: str, max_concurrent: int) -> asyncio.Semaphore:
        """Get or create semaphore for a route."""
        if route not in self._semaphores:
            self._semaphores[route] = asyncio.Semaphore(max_concurrent)
        return self._semaphores[route]
    
    async def acquire(self, route: str, max_concurrent: int) -> None:
        """Acquire semaphore for route."""
        sem = self.get_semaphore(route, max_concurrent)
        await sem.acquire()
    
    async def release(self, route: str, max_concurrent: int) -> None:
        """Release semaphore for route."""
        sem = self.get_semaphore(route, max_concurrent)
        sem.release()


# Global semaphore manager
semaphore_manager = RouteSemaphore()
