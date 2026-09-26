"""Dataset exporters."""

import json
import os
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel

from app.config import settings


class ExportManifest(BaseModel):
    """Export manifest."""

    version_id: str
    format: str
    filters: Dict[str, Any]
    template: Optional[str] = None
    tokenizer: Optional[str] = None
    hashes: Dict[str, str]


class Exporter:
    """Base exporter class."""

    def __init__(self, dataset_id: str, version_id: str):
        self.dataset_id = dataset_id
        self.version_id = version_id

    async def export(self) -> str:
        """Export dataset and return path."""
        raise NotImplementedError


class JSONLExporter(Exporter):
    """JSONL exporter."""

    async def export(self) -> str:
        """Export to JSONL format."""
        # TODO: Load records from Lance
        records = []  # placeholder

        output_path = f"/tmp/{self.dataset_id}_{self.version_id}.jsonl"
        with open(output_path, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

        return output_path


class ParquetExporter(Exporter):
    """Parquet exporter."""

    async def export(self) -> str:
        """Export to Parquet format."""
        # TODO: Load records from Lance
        records = []  # placeholder

        output_path = f"/tmp/{self.dataset_id}_{self.version_id}.parquet"
        df = pd.DataFrame(records)
        df.to_parquet(output_path, index=False)

        return output_path


class HFDatasetExporter(Exporter):
    """HuggingFace dataset exporter."""

    async def export(self) -> str:
        """Export to HF dataset format."""
        # TODO: Load records from Lance
        records = []  # placeholder

        output_path = f"/tmp/{self.dataset_id}_{self.version_id}"
        os.makedirs(output_path, exist_ok=True)

        # Export to Parquet shards
        df = pd.DataFrame(records)
        df.to_parquet(f"{output_path}/data/train-00000-of-00001.parquet", index=False)

        # Create dataset_info.json
        with open(f"{output_path}/dataset_info.json", "w") as f:
            json.dump({"description": "Exported from Forge"}, f)

        return output_path


class ShareGPTExporter(Exporter):
    """ShareGPT exporter."""

    async def export(self) -> str:
        """Export to ShareGPT format."""
        # TODO: Load records from Lance
        records = []  # placeholder

        output_path = f"/tmp/{self.dataset_id}_{self.version_id}_sharegpt.jsonl"
        with open(output_path, "w") as f:
            for record in records:
                messages = record.get("messages", [])
                if messages:
                    f.write(json.dumps({"conversations": messages}) + "\n")

        return output_path


class ChatMLExporter(Exporter):
    """ChatML exporter."""

    async def export(self) -> str:
        """Export to ChatML format."""
        # TODO: Load records from Lance
        records = []  # placeholder

        output_path = f"/tmp/{self.dataset_id}_{self.version_id}_chatml.jsonl"
        with open(output_path, "w") as f:
            for record in records:
                messages = record.get("messages", [])
                chatml = "\n".join(
                    f"<|{m['role']}|>\n{m['content']}\n"
                    for m in messages
                )
                f.write(chatml + "\n")

        return output_path


class DPOExporter(Exporter):
    """DPO exporter."""

    async def export(self) -> str:
        """Export to DPO format."""
        # TODO: Load DPO pairs
        pairs = []  # placeholder

        output_path = f"/tmp/{self.dataset_id}_{self.version_id}_dpo.jsonl"
        with open(output_path, "w") as f:
            for pair in pairs:
                f.write(json.dumps({
                    "prompt": pair.get("prompt", ""),
                    "chosen": pair.get("chosen", ""),
                    "rejected": pair.get("rejected", ""),
                }) + "\n")

        return output_path


# Exporter factory
EXPORTERS = {
    "jsonl": JSONLExporter,
    "parquet": ParquetExporter,
    "hf": HFDatasetExporter,
    "sharegpt": ShareGPTExporter,
    "chatml": ChatMLExporter,
    "dpo": DPOExporter,
}


def get_exporter(format: str, dataset_id: str, version_id: str) -> Exporter:
    """Get exporter instance."""
    exporter_cls = EXPORTERS.get(format)
    if not exporter_cls:
        raise ValueError(f"Unknown format: {format}")
    return exporter_cls(dataset_id, version_id)
