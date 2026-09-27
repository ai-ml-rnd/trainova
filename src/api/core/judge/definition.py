"""Judge definitions for LLM-as-judge."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class JudgeDefinition(BaseModel):
    """Judge definition."""
    
    id: str
    name: str
    description: Optional[str] = None
    judge_type: str  # pointwise, pairwise, rank
    rubric: Dict


class PointwiseRubric(BaseModel):
    """Pointwise rubric for scoring."""
    
    criteria: List[Dict]
    scale_min: int = 1
    scale_max: int = 10
    anchors: Optional[Dict[int, str]] = None


class PairwiseRubric(BaseModel):
    """Pairwise rubric for comparison."""
    
    criteria: List[Dict]
    position_swap: bool = True


class JudgeRegistry:
    """Registry for judge definitions."""
    
    def __init__(self):
        self._judges: Dict[str, JudgeDefinition] = {}
    
    def register(self, judge: JudgeDefinition) -> None:
        """Register a judge."""
        self._judges[judge.id] = judge
    
    def get(self, judge_id: str) -> JudgeDefinition:
        """Get judge by ID."""
        if judge_id not in self._judges:
            raise ValueError(f"Judge not found: {judge_id}")
        return self._judges[judge_id]
    
    def list(self) -> List[JudgeDefinition]:
        """List all judges."""
        return list(self._judges.values())


# Global registry
judge_registry = JudgeRegistry()

# Default judges
judge_registry.register(JudgeDefinition(
    id="default_pointwise",
    name="Default Pointwise",
    judge_type="pointwise",
    rubric=PointwiseRubric(
        criteria=[{"name": "quality", "description": "Overall quality"}],
        scale_min=1,
        scale_max=10,
        anchors={1: "Poor", 5: "Fair", 10: "Excellent"},
    ).model_dump(),
))

judge_registry.register(JudgeDefinition(
    id="default_pairwise",
    name="Default Pairwise",
    judge_type="pairwise",
    rubric=PairwiseRubric(
        criteria=[{"name": "preference", "description": "Prefer one response"}],
        position_swap=True,
    ).model_dump(),
))
