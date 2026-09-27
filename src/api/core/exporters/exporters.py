"""Dataset exporters."""

from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel
import json
import pandas as pd


class ExportFormat(str, Enum):
    """Export format enum."""
    
    JSONL = "jsonl"
    PARQUET = "parquet"
    HF_DATASETS = "hf"
    DPO = "dpo"
    CHATML = "chatml"
    ALPACA = "alpaca"
    SHAREGPT = "sharegpt"


class Exporter(BaseModel):
    """Dataset exporter."""
    
    format: ExportFormat
    
    def export(self, records: List[Dict], path: str) -> None:
        """Export records to file."""
        raise NotImplementedError


class JSONLExporter(Exporter):
    """JSONL exporter."""
    
    format: ExportFormat = ExportFormat.JSONL
    
    def export(self, records: List[Dict], path: str) -> None:
        """Export to JSONL."""
        with open(path, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")


class ParquetExporter(Exporter):
    """Parquet exporter."""
    
    format: ExportFormat = ExportFormat.PARQUET
    
    def export(self, records: List[Dict], path: str) -> None:
        """Export to Parquet."""
        df = pd.DataFrame(records)
        df.to_parquet(path)


class HFExporter(Exporter):
    """Hugging Face datasets exporter."""
    
    format: ExportFormat = ExportFormat.HF_DATASETS
    
    def export(self, records: List[Dict], path: str) -> None:
        """Export to HF datasets format."""
        # For MVP, export as JSONL and let HF load it
        jsonl_path = path.replace(".hf", ".jsonl")
        self.export(records, jsonl_path)


class DPOExporter(Exporter):
    """DPO trainer exporter."""
    
    format: ExportFormat = ExportFormat.DPO
    
    def export(self, records: List[Dict], path: str) -> None:
        """Export in DPO format."""
        with open(path, "w") as f:
            for record in records:
                dpo_record = {
                    "prompt": record.get("prompt", ""),
                    "chosen": record.get("chosen_response", ""),
                    "rejected": record.get("rejected_response", ""),
                }
                f.write(json.dumps(dpo_record) + "\n")


class ExporterRegistry:
    """Registry for exporters."""
    
    def __init__(self):
        self._exporters: Dict[ExportFormat, Exporter] = {}
    
    def register(self, exporter: Exporter) -> None:
        """Register an exporter."""
        self._exporters[exporter.format] = exporter
    
    def get(self, format: ExportFormat) -> Exporter:
        """Get exporter by format."""
        if format not in self._exporters:
            raise ValueError(f"Exporter not found: {format}")
        return self._exporters[format]
    
    def list(self) -> List[Exporter]:
        """List all exporters."""
        return list(self._exporters.values())


# Global registry
exporter_registry = ExporterRegistry()
exporter_registry.register(JSONLExporter())
exporter_registry.register(ParquetExporter())
exporter_registry.register(HFExporter())
exporter_registry.register(DPOExporter())
