"""Per-mixture tokenizer stats."""

from typing import List, Dict
from collections import Counter


class TokenizerStats:
    """Calculate tokenizer statistics."""
    
    def __init__(self):
        self._token_counts = Counter()
    
    def add_text(self, text: str) -> None:
        """Add text to stats."""
        tokens = text.split()
        self._token_counts.update(tokens)
    
    def get_stats(self) -> Dict:
        """Get tokenizer statistics."""
        return {
            "vocab_size": len(self._token_counts),
            "total_tokens": sum(self._token_counts.values()),
            "unique_tokens": len(self._token_counts),
            "top_tokens": self._token_counts.most_common(100),
        }
    
    def reset(self) -> None:
        """Reset stats."""
        self._token_counts.clear()


def calculate_mixture_stats(documents: List[Dict]) -> Dict:
    """Calculate tokenizer stats for a mixture."""
    stats = TokenizerStats()
    
    for doc in documents:
        stats.add_text(doc.get("text", ""))
    
    return stats.get_stats()
