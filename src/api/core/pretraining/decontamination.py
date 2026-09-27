"""n-gram decontamination vs eval sets."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class EvalSet(BaseModel):
    """Evaluation set."""
    
    name: str
    ngrams: List[str]


class Decontaminator:
    """Decontamination checker."""
    
    def __init__(self, ngram_size: int = 8):
        self.ngram_size = ngram_size
    
    def extract_ngrams(self, text: str) -> List[str]:
        """Extract n-grams from text."""
        words = text.split()
        return [
            " ".join(words[i:i + self.ngram_size])
            for i in range(len(words) - self.ngram_size + 1)
        ]
    
    def is_contaminated(
        self,
        text: str,
        eval_sets: List[EvalSet],
    ) -> bool:
        """Check if text is contaminated by eval sets."""
        text_ngrams = set(self.extract_ngrams(text))
        
        for eval_set in eval_sets:
            eval_ngrams = set(eval_set.ngrams)
            if text_ngrams & eval_ngrams:
                return True
        
        return False
    
    def filter_contaminated(
        self,
        documents: List[Dict],
        eval_sets: List[EvalSet],
    ) -> List[Dict]:
        """Filter out contaminated documents."""
        return [
            doc for doc in documents
            if not self.is_contaminated(doc.get("text", ""), eval_sets)
        ]


def decontaminate(
    documents: List[Dict],
    eval_sets: List[EvalSet],
) -> List[Dict]:
    """Decontaminate documents vs eval sets."""
    decontaminator = Decontaminator()
    return decontaminator.filter_contaminated(documents, eval_sets)
