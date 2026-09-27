"""Review adjudication and consensus resolution."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class AdjudicationRecord(BaseModel):
    """Adjudication record."""
    
    task_id: str
    original_answers: List[Dict]
    adjudicated_answer: str
    adjudicated_by: str
    timestamp: str


class AdjudicationService:
    """Adjudication service for consensus resolution."""
    
    def __init__(self):
        self._adjudications: Dict[str, AdjudicationRecord] = {}
    
    async def adjudicate(
        self,
        task_id: str,
        original_answers: List[Dict],
        adjudicated_by: str,
    ) -> AdjudicationRecord:
        """Adjudicate conflicting annotations."""
        # Determine consensus
        answer_counts = {}
        for answer in original_answers:
            ans = answer.get("answer", "")
            answer_counts[ans] = answer_counts.get(ans, 0) + 1
        
        # Majority vote
        majority = max(answer_counts, key=answer_counts.get)
        
        record = AdjudicationRecord(
            task_id=task_id,
            original_answers=original_answers,
            adjudicated_answer=majority,
            adjudicated_by=adjudicated_by,
            timestamp="2026-09-27T00:00:00Z",
        )
        
        self._adjudications[task_id] = record
        return record
    
    async def override(
        self,
        task_id: str,
        new_answer: str,
        adjudicated_by: str,
    ) -> AdjudicationRecord:
        """Override adjudication with new answer."""
        record = AdjudicationRecord(
            task_id=task_id,
            original_answers=[{"answer": new_answer}],
            adjudicated_answer=new_answer,
            adjudicated_by=adjudicated_by,
            timestamp="2026-09-27T00:00:00Z",
        )
        
        self._adjudications[task_id] = record
        return record
    
    async def get_adjudication(self, task_id: str) -> Optional[AdjudicationRecord]:
        """Get adjudication record."""
        return self._adjudications.get(task_id)
    
    async def get_canonical_response(self, task_id: str) -> Optional[str]:
        """Get canonical response for task."""
        record = await self.get_adjudication(task_id)
        if record:
            return record.adjudicated_answer
        return None


# Global service instance
adjudication_service = AdjudicationService()
