"""DPO pair builder service."""

from typing import Dict, List, Optional

from pydantic import BaseModel

from app.config import settings


class DPOPair(BaseModel):
    """DPO pair."""

    prompt: str
    chosen: str
    rejected: str
    judge_score: float
    margin: float


class DPOMarginCalculator:
    """Calculate margin between chosen and rejected responses."""

    @staticmethod
    def calculate_margin(chosen_score: float, rejected_score: float) -> float:
        """Calculate margin between scores."""
        return chosen_score - rejected_score


class DPOPairBuilder:
    """Build DPO pairs from judge results."""

    def __init__(self, margin_threshold: float = 0.5):
        self.margin_threshold = margin_threshold

    def build_pairs(
        self,
        judge_results: List[Dict[str, Any]],
    ) -> List[DPOPair]:
        """Build DPO pairs from judge results."""
        pairs = []

        for result in judge_results:
            scores = result.get("scores", {})
            prompt = result.get("prompt", "")

            # Extract chosen and rejected
            chosen = scores.get("chosen", "")
            rejected = scores.get("rejected", "")

            if not chosen or not rejected:
                continue

            # Calculate margin
            chosen_score = scores.get("chosen_score", 0)
            rejected_score = scores.get("rejected_score", 0)
            margin = DPOMarginCalculator.calculate_margin(chosen_score, rejected_score)

            # Only include pairs above margin threshold
            if margin >= self.margin_threshold:
                pairs.append(
                    DPOPair(
                        prompt=prompt,
                        chosen=chosen,
                        rejected=rejected,
                        judge_score=chosen_score,
                        margin=margin,
                    )
                )

        return pairs

    def filter_low_margin(
        self,
        judge_results: List[Dict[str, Any]],
    ) -> tuple[List[DPOPair], List[Dict[str, Any]]]:
        """Filter judge results into high-margin pairs and low-margin for annotation."""
        high_margin = []
        low_margin = []

        for result in judge_results:
            scores = result.get("scores", {})
            chosen_score = scores.get("chosen_score", 0)
            rejected_score = scores.get("rejected_score", 0)
            margin = DPOMarginCalculator.calculate_margin(chosen_score, rejected_score)

            if margin >= self.margin_threshold:
                high_margin.append(result)
            else:
                low_margin.append(result)

        return high_margin, low_margin


# Global instance
_dpo_builder = DPOPairBuilder(margin_threshold=0.5)


def get_dpo_builder() -> DPOPairBuilder:
    """Get the global DPO builder."""
    return _dpo_builder


async def build_dpo_pairs(
    judge_results: List[Dict[str, Any]],
    margin_threshold: float = 0.5,
) -> List[DPOPair]:
    """Build DPO pairs from judge results."""
    builder = DPOPairBuilder(margin_threshold=margin_threshold)
    return builder.build_pairs(judge_results)


async def get_low_margin_for_annotation(
    judge_results: List[Dict[str, Any]],
    margin_threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """Get low-margin results for annotation."""
    builder = DPOPairBuilder(margin_threshold=margin_threshold)
    _, low_margin = builder.filter_low_margin(judge_results)
    return low_margin
