"""DataTrove operator adapters."""

from typing import List

import pyarrow as pa

from core.curation.operator import (
    FilterOperator,
    Operator,
    OperatorKind,
    OpContext,
)


class GopherQualityFilter(FilterOperator):
    """DataTrove Gopher quality filter adapter."""
    
    name: str = "gopher_quality_filter"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.FILTER
    
    def __init__(self, min_words: int = 50, max_words: int = 100000):
        self.min_words = min_words
        self.max_words = max_words
    
    def filter(self, batch: pa.RecordBatch) -> pa.RecordBatch:
        """Filter based on word count."""
        # Assuming 'text' column exists
        if 'text' not in batch.column_names:
            return batch
        
        texts = batch.column('text').to_pylist()
        mask = []
        reject_reasons = []
        
        for text in texts:
            word_count = len(text.split()) if text else 0
            if self.min_words <= word_count <= self.max_words:
                mask.append(True)
                reject_reasons.append(None)
            else:
                mask.append(False)
                reject_reasons.append(f"word_count={word_count} not in [{self.min_words}, {self.max_words}]")
        
        # Add reject_reason column
        batch = batch.append_column('reject_reason', pa.array(reject_reasons))
        
        return batch.filter(mask)


class C4Filter(FilterOperator):
    """DataTrove C4 quality filter adapter."""
    
    name: str = "c4_filter"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.FILTER
    
    def __init__(self, min_chars: int = 100, max_chars: int = 100000):
        self.min_chars = min_chars
        self.max_chars = max_chars
    
    def filter(self, batch: pa.RecordBatch) -> pa.RecordBatch:
        """Filter based on character count."""
        if 'text' not in batch.column_names:
            return batch
        
        texts = batch.column('text').to_pylist()
        mask = []
        reject_reasons = []
        
        for text in texts:
            char_count = len(text) if text else 0
            if self.min_chars <= char_count <= self.max_chars:
                mask.append(True)
                reject_reasons.append(None)
            else:
                mask.append(False)
                reject_reasons.append(f"char_count={char_count} not in [{self.min_chars}, {self.max_chars}]")
        
        batch = batch.append_column('reject_reason', pa.array(reject_reasons))
        return batch.filter(mask)


class FineWebFilter(FilterOperator):
    """DataTrove FineWeb quality filter adapter."""
    
    name: str = "fineweb_filter"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.FILTER
    
    def __init__(self, min_score: float = 0.5):
        self.min_score = min_score
    
    def filter(self, batch: pa.RecordBatch) -> pa.RecordBatch:
        """Filter based on quality score."""
        if 'quality_score' not in batch.column_names:
            return batch
        
        scores = batch.column('quality_score').to_pylist()
        mask = []
        reject_reasons = []
        
        for score in scores:
            if score >= self.min_score:
                mask.append(True)
                reject_reasons.append(None)
            else:
                mask.append(False)
                reject_reasons.append(f"quality_score={score} < {self.min_score}")
        
        batch = batch.append_column('reject_reason', pa.array(reject_reasons))
        return batch.filter(mask)


def register_datatrove_operators(registry) -> None:
    """Register DataTrove adapters with registry."""
    registry.register(GopherQualityFilter())
    registry.register(C4Filter())
    registry.register(FineWebFilter())
