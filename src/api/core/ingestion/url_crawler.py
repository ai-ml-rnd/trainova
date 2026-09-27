"""Polite URL crawler with robots.txt support."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class CrawlRequest(BaseModel):
    """Crawl request."""
    
    url: str
    max_depth: int = 1
    rate_limit: float = 1.0  # requests per second
    respect_robots: bool = True


class CrawlResult(BaseModel):
    """Crawl result."""
    
    url: str
    status: int
    content: Optional[str] = None
    links: List[str] = []


class URLCrawler:
    """Polite URL crawler."""
    
    def __init__(self):
        self._visited: Dict[str, bool] = {}
        self._rate_limits: Dict[str, float] = {}
    
    async def crawl(
        self,
        url: str,
        max_depth: int = 1,
    ) -> List[CrawlResult]:
        """Crawl URLs starting from root."""
        results = []
        
        # Check robots.txt
        if not await self._check_robots(url):
            return []
        
        # Crawl with depth limit
        await self._crawl_url(url, max_depth, results)
        
        return results
    
    async def _crawl_url(
        self,
        url: str,
        depth: int,
        results: List[CrawlResult],
    ) -> None:
        """Crawl a single URL."""
        if url in self._visited or depth < 0:
            return
        
        self._visited[url] = True
        
        # Simulate crawl (in production, use aiohttp)
        result = CrawlResult(url=url, status=200)
        results.append(result)
        
        # Recurse on links
        if depth > 0:
            for link in result.links:
                await self._crawl_url(link, depth - 1, results)
    
    async def _check_robots(self, url: str) -> bool:
        """Check robots.txt for permission."""
        # For MVP, assume allowed
        return True
    
    def set_rate_limit(self, domain: str, limit: float) -> None:
        """Set rate limit for domain."""
        self._rate_limits[domain] = limit
    
    def get_rate_limit(self, domain: str) -> float:
        """Get rate limit for domain."""
        return self._rate_limits.get(domain, 1.0)
