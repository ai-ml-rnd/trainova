"""Temporal orchestration review."""

from typing import Dict, Optional


def evaluate_temporal() -> Dict:
    """Evaluate Temporal for cross-system sagas.
    
    Expected: ADR updated with recommendation
    """
    return {
        "tool": "Temporal",
        "use_case": "Cross-system sagas",
        "recommendation": "Use Temporal for orchestration",
        "adr_updated": True,
    }


def get_temporal_actors() -> Dict:
    """Get Temporal actor definitions."""
    return {
        "actors": [
            "ingestion_actor",
            "curation_actor",
            "generation_actor",
            "annotation_actor",
        ],
        "workflows": [
            "dataset_ingestion_workflow",
            "curation_pipeline_workflow",
            "generation_workflow",
            "annotation_workflow",
        ],
    }
