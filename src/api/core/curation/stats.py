"""Token and quality statistics."""

from typing import List, Dict

import pyarrow as pa

from core.curation.operator import MapperOperator, OperatorKind, OpContext


class TokenStatsMapper(MapperOperator):
    """Token statistics mapper."""
    
    name: str = "token_stats"
    version: str = "1.0"
    kind = OperatorKind.MAPPER
    
    def __init__(self, tokenizer_name: str = "gpt2"):
        self.tokenizer_name = tokenizer_name
        self._tokenizer = None
    
    def _get_tokenizer(self):
        """Get tokenizer (placeholder for tiktoken)."""
        if self._tokenizer is None:
            if self.tokenizer_name == "gpt2":
                # Use simple word-based tokenization for MVP
                self._tokenizer = "gpt2"
            else:
                self._tokenizer = self.tokenizer_name
        return self._tokenizer
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (simple word-based for MVP)."""
        return len(text.split())
    
    def map(self, batch: pa.RecordBatch) -> pa.RecordBatch:
        """Add token count column."""
        if "text" not in batch.column_names:
            return batch
        
        texts = batch.column("text").to_pylist()
        token_counts = [self.count_tokens(t) for t in texts]
        
        return batch.append_column("token_count", pa.array(token_counts))
    
    def compute_histogram(self, token_counts: List[int], num_buckets: int = 100) -> Dict:
        """Compute token count histogram."""
        if not token_counts:
            return {"buckets": [], "counts": []}
        
        max_count = max(token_counts)
        bucket_size = max_count // num_buckets + 1
        
        buckets = [i * bucket_size for i in range(num_buckets + 1)]
        counts = [0] * num_buckets
        
        for count in token_counts:
            bucket_idx = min(count // bucket_size, num_buckets - 1)
            counts[bucket_idx] += 1
        
        return {
            "buckets": buckets,
            "counts": counts,
            "min": min(token_counts),
            "max": max(token_counts),
            "avg": sum(token_counts) / len(token_counts),
            "total": len(token_counts),
        }


class QualityMetricsMapper(MapperOperator):
    """Quality metrics mapper."""
    
    name: str = "quality_metrics"
    version: str = "1.0"
    kind = OperatorKind.MAPPER
    
    def __init__(
        self,
        min_words: int = 50,
        max_words: int = 100000,
        min_chars: int = 100,
        max_chars: int = 100000,
    ):
        self.min_words = min_words
        self.max_words = max_words
        self.min_chars = min_chars
        self.max_chars = max_chars
    
    def compute_quality_score(self, text: str) -> float:
        """Compute quality score (0-1)."""
        if not text:
            return 0.0
        
        word_count = len(text.split())
        char_count = len(text)
        
        score = 0.0
        
        # Word count score
        if self.min_words <= word_count <= self.max_words:
            score += 0.4
        
        # Character count score
        if self.min_chars <= char_count <= self.max_chars:
            score += 0.3
        
        # Length ratio (avoid very short or very long)
        length_ratio = min(word_count / 1000, 1.0)
        score += 0.3 * length_ratio
        
        return score
    
    def map(self, batch: pa.RecordBatch) -> pa.RecordBatch:
        """Add quality score column."""
        if "text" not in batch.column_names:
            return batch
        
        texts = batch.column("text").to_pylist()
        quality_scores = [self.compute_quality_score(t) for t in texts]
        
        return batch.append_column("quality_score", pa.array(quality_scores))


def register_stats_operators(registry):
    """Register stats operators."""
    registry.register(TokenStatsMapper())
    registry.register(QualityMetricsMapper())
