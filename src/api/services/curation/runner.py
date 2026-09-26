"""Curation pipeline runner."""

from typing import List, Optional

import pyarrow as pa

from services.curation.data_trove_adapters import (
    LanguageIDFilter,
    HeuristicQualityFilter,
    PIIRegexFilter,
    TokenCounter,
)
from services.curation.operators import OpContext


class CurationRunner:
    """Run curation pipeline on a dataset."""

    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.operators: list = []

    def add_operator(self, operator):
        """Add an operator to the pipeline."""
        self.operators.append(operator)
        return self

    async def run(self, batch_size: int = 1000) -> dict:
        """Run the curation pipeline."""
        ctx = OpContext(dataset_id=self.dataset_id, step="curation")

        # TODO: Load dataset from Lance
        # TODO: Process in batches
        # TODO: Write results back to Lance

        return {
            "dataset_id": self.dataset_id,
            "operators_applied": [op.name for op in self.operators],
            "records_processed": 0,
            "records_rejected": 0,
            "stage_manifests": [],
        }


# Pre-built curation recipes
def language_id_pipeline(dataset_id: str, languages: Optional[list[str]] = None):
    """Create a language ID pipeline."""
    runner = CurationRunner(dataset_id)
    runner.add_operator(LanguageIDFilter(languages=languages))
    return runner


def quality_filter_pipeline(dataset_id: str):
    """Create a quality filter pipeline."""
    runner = CurationRunner(dataset_id)
    runner.add_operator(HeuristicQualityFilter())
    runner.add_operator(PIIRegexFilter())
    return runner


def full_curation_pipeline(dataset_id: str):
    """Create a full curation pipeline."""
    runner = CurationRunner(dataset_id)
    runner.add_operator(LanguageIDFilter())
    runner.add_operator(HeuristicQualityFilter())
    runner.add_operator(PIIRegexFilter())
    runner.add_operator(TokenCounter())
    return runner
