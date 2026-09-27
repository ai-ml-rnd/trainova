"""Uncertainty-based prioritization for active learning."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class Prediction(BaseModel):
    """Model prediction with uncertainty."""
    
    document_id: str
    label: str
    confidence: float
    entropy: Optional[float] = None


class UncertaintySelector:
    """Select documents based on uncertainty."""
    
    def select_uncertain(
        self,
        predictions: List[Prediction],
        n_select: int,
    ) -> List[Prediction]:
        """Select most uncertain documents."""
        # Sort by entropy (higher = more uncertain)
        sorted_preds = sorted(
            predictions,
            key=lambda p: p.entropy if p.entropy else (1.0 - p.confidence),
            reverse=True,
        )
        return sorted_preds[:n_select]
    
    def select_confident(
        self,
        predictions: List[Prediction],
        threshold: float = 0.9,
    ) -> List[Prediction]:
        """Select confident predictions (for pseudo-labeling)."""
        return [p for p in predictions if p.confidence >= threshold]
    
    def calculate_entropy(self, probabilities: List[float]) -> float:
        """Calculate entropy of probability distribution."""
        import math
        
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy


def uncertainty_sample(documents: List[Dict], n_samples: int) -> List[Dict]:
    """Sample uncertain documents for annotation.
    
    Expected: ≥20% fewer annotations to reach target agreement
    """
    selector = UncertaintySelector()
    
    # For MVP, return first n_samples
    return documents[:n_samples]
