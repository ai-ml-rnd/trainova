"""DPO pair builder from judge responses."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class DPOPair(BaseModel):
    """DPO training pair."""
    
    prompt: str
    chosen: str
    rejected: str
    margin: float


class DPOPairBuilder:
    """Build DPO pairs from judge responses."""
    
    def __init__(self, margin_threshold: float = 0.5):
        self.margin_threshold = margin_threshold
        self._pairs: List[DPOPair] = []
    
    def build_pairs(
        self,
        judge_responses: List[Dict],
    ) -> List[DPOPair]:
        """Build DPO pairs from judge responses.
        
        Args:
            judge_responses: List of judge responses with chosen/rejected
            
        Returns:
            List of DPO pairs
        """
        pairs = []
        
        for response in judge_responses:
            prompt = response.get("prompt", "")
            chosen = response.get("chosen", "")
            rejected = response.get("rejected", "")
            margin = response.get("margin", 0.0)
            
            # Only include if margin is significant
            if abs(margin) >= self.margin_threshold:
                pairs.append(DPOPair(
                    prompt=prompt,
                    chosen=chosen,
                    rejected=rejected,
                    margin=margin,
                ))
        
        self._pairs = pairs
        return pairs
    
    def get_low_margin_pairs(self) -> List[DPOPair]:
        """Get pairs with low margin (should be sent to annotation queue)."""
        return [
            p for p in self._pairs
            if abs(p.margin) < self.margin_threshold
        ]
    
    def export_for_trl(self) -> List[Dict]:
        """Export pairs in TRL DPOTrainer format."""
        return [
            {
                "prompt": p.prompt,
                "chosen": p.chosen,
                "rejected": p.rejected,
            }
            for p in self._pairs
        ]
