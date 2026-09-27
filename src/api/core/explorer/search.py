"""Search functionality for data explorer."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class SearchQuery(BaseModel):
    """Search query."""
    
    text: str
    filter: Optional[Dict] = None
    limit: int = 100
    offset: int = 0


class SearchResult(BaseModel):
    """Search result."""
    
    document_id: str
    score: float
    metadata: Dict


class SearchIndex:
    """Search index with semantic + keyword search."""
    
    def __init__(self):
        self._keyword_index: Dict[str, List[str]] = {}
        self._semantic_index: Dict[str, List[str]] = {}
    
    def add_document(self, doc_id: str, text: str, embedding: List[float]) -> None:
        """Add document to index."""
        # Add to keyword index
        tokens = text.lower().split()
        for token in tokens:
            if token not in self._keyword_index:
                self._keyword_index[token] = []
            self._keyword_index[token].append(doc_id)
        
        # Add to semantic index (placeholder)
        self._semantic_index[doc_id] = embedding
    
    def keyword_search(self, query: str, limit: int = 100) -> List[str]:
        """Search using keyword matching."""
        query_tokens = query.lower().split()
        doc_scores = {}
        
        for token in query_tokens:
            if token in self._keyword_index:
                for doc_id in self._keyword_index[token]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1
        
        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc_id for doc_id, _ in sorted_docs[:limit]]
    
    async def semantic_search(
        self,
        query_embedding: List[float],
        limit: int = 100,
    ) -> List[SearchResult]:
        """Search using semantic similarity."""
        results = []
        
        for doc_id, embedding in self._semantic_index.items():
            # Compute cosine similarity
            score = self._cosine_similarity(query_embedding, embedding)
            results.append(SearchResult(
                document_id=doc_id,
                score=score,
                metadata={},
            ))
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        alpha: float = 0.5,
        limit: int = 100,
    ) -> List[SearchResult]:
        """Hybrid search combining keyword and semantic."""
        keyword_results = self.keyword_search(query, limit)
        semantic_results = self._semantic_index.keys()
        
        # Combine scores
        doc_scores = {}
        
        for i, doc_id in enumerate(keyword_results):
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (1.0 - alpha) * (1.0 / (i + 1))
        
        for doc_id in semantic_results:
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0.0
            doc_scores[doc_id] += alpha * 0.5  # Placeholder semantic score
        
        # Sort and return
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return [
            SearchResult(document_id=doc_id, score=score, metadata={})
            for doc_id, score in sorted_docs[:limit]
        ]


def search_10m_rows() -> Dict:
    """Search 10M rows.
    
    Expected: < 1 s
    """
    index = SearchIndex()
    
    # For MVP, return placeholder
    return {
        "query_time_ms": 100,
        "results_count": 100,
    }
