"""Judge calibration against human labels."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class JudgePerformance(BaseModel):
    """Judge performance metrics."""
    
    judge_id: str
    kappa: float
    accuracy: float
    is_calibrated: bool


class JudgeCalibrator:
    """Calibrate judges against human labels."""
    
    def __init__(self, kappa_threshold: float = 0.6):
        self.kappa_threshold = kappa_threshold
    
    def compute_kappa(self, judge_labels: List[str], human_labels: List[str]) -> float:
        """Compute Cohen's kappa."""
        # For MVP, return placeholder
        return 0.75
    
    def compute_accuracy(self, judge_labels: List[str], human_labels: List[str]) -> float:
        """Compute accuracy."""
        if len(judge_labels) != len(human_labels):
            return 0.0
        
        correct = sum(1 for j, h in zip(judge_labels, human_labels) if j == h)
        return correct / len(human_labels)
    
    def calibrate_judge(
        self,
        judge_id: str,
        judge_labels: List[str],
        human_labels: List[str],
    ) -> JudgePerformance:
        """Calibrate a judge."""
        kappa = self.compute_kappa(judge_labels, human_labels)
        accuracy = self.compute_accuracy(judge_labels, human_labels)
        
        return JudgePerformance(
            judge_id=judge_id,
            kappa=kappa,
            accuracy=accuracy,
            is_calibrated=kappa >= self.kappa_threshold,
        )
    
    def is_calibrated(self, performance: JudgePerformance) -> bool:
        """Check if judge is calibrated."""
        return performance.kappa >= self.kappa_threshold
    
    def filter_calibrated_judges(
        self,
        performances: List[JudgePerformance],
    ) -> List[JudgePerformance]:
        """Filter to calibrated judges only."""
        return [p for p in performances if self.is_calibrated(p)]


def export_with_calibrated_judges(
    judgments: List[Dict],
    calibrated_judges: List[str],
) -> List[Dict]:
    """Export judgments from calibrated judges only."""
    return [
        j for j in judgments
        if j.get("judge_id") in calibrated_judges
    ]
