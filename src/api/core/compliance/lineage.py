"""Per-export lineage report."""

from typing import List, Dict
from pydantic import BaseModel


class LineageRecord(BaseModel):
    """Lineage record for export."""
    
    export_id: str
    sources: List[str]
    licenses: List[str]
    models: List[str]
    annotators: List[str]


class LineageReporter:
    """Reporter for export lineage."""
    
    def __init__(self):
        self._records: Dict[str, LineageRecord] = {}
    
    def create_lineage(
        self,
        export_id: str,
        sources: List[str],
        licenses: List[str],
        models: List[str],
        annotators: List[str],
    ) -> LineageRecord:
        """Create lineage record for export."""
        record = LineageRecord(
            export_id=export_id,
            sources=sources,
            licenses=licenses,
            models=models,
            annotators=annotators,
        )
        
        self._records[export_id] = record
        return record
    
    def get_lineage(self, export_id: str) -> LineageRecord:
        """Get lineage record for export."""
        return self._records.get(export_id)
    
    def get_all_lineage(self) -> List[LineageRecord]:
        """Get all lineage records."""
        return list(self._records.values())


def create_lineage_report(
    export_id: str,
    sources: List[str],
    licenses: List[str],
    models: List[str],
    annotators: List[str],
) -> Dict:
    """Create lineage report for export.
    
    Expected: Sources, licenses, models, annotators
    """
    reporter = LineageReporter()
    record = reporter.create_lineage(export_id, sources, licenses, models, annotators)
    
    return record.dict()
