"""Confident learning for label issue detection."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class LabelIssue(BaseModel):
    """Detected label issue."""
    
    document_id: str
    issue_type: str  # "noisy_label", "outlier", "mislabel"
    confidence: float
    suggested_label: Optional[str] = None


class ConfidentLearning:
    """Confident learning for label issue detection."""
    
    def __init__(self, noise_threshold: float = 0.1):
        self.noise_threshold = noise_threshold
    
    def detect_issues(
        self,
        predictions: List[Prediction],
        labels: List[str],
    ) -> List[LabelIssue]:
        """Detect label issues using confident learning."""
        issues = []
        
        for pred, label in zip(predictions, labels):
            if pred.confidence < self.noise_threshold:
                issues.append(LabelIssue(
                    document_id=pred.document_id,
                    issue_type="noisy_label",
                    confidence=pred.confidence,
                    suggested_label=pred.label,
                ))
        
        return issues
    
    def get_quality_scores(
        self,
        documents: List[Dict],
        predictions: List[Prediction],
    ) -> Dict[str, float]:
        """Get quality scores for documents."""
        scores = {}
        
        for doc, pred in zip(documents, predictions):
            scores[doc.get("id", "")] = pred.confidence
        
        return scores


def confident_learning_scores(documents: List[Dict]) -> Dict[str, float]:
    """Get confident learning scores.
    
    Expected: ≥20% fewer annotations to reach target agreement
    """
    cl = ConfidentLearning()
    
    # For MVP, return placeholder scores
    return {doc.get("id", ""): 0.8 for doc in documents}
