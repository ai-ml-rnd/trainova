"""JSONL file connector."""

import json
from typing import List, Optional

from core.record_store import Record
from core.connector.base import SourceConnector


class JSONLConnector(SourceConnector):
    """Connector for JSONL files."""
    
    name: str = "jsonl"
    
    def __init__(self):
        self._file = None
        self._current_line = 0
        self._path: Optional[str] = None
    
    async def connect(self, source: str) -> None:
        """Connect to JSONL file."""
        self._path = source
        self._file = open(source, "r")
        self._current_line = 0
    
    async def read_batch(self, batch_size: int) -> List[Record]:
        """Read a batch of records."""
        records = []
        
        for _ in range(batch_size):
            line = self._file.readline()
            if not line:
                break
            
            data = json.loads(line)
            record = Record(
                record_id=data.get("record_id", f"line-{self._current_line}"),
                fields=data.get("fields", {}),
                metadata=data.get("metadata", {}),
                provenance=data.get("provenance", []),
                quality=data.get("quality", {}),
                status=data.get("status", "pending"),
                reject_reason=data.get("reject_reason"),
                embedding=data.get("embedding"),
            )
            records.append(record)
            self._current_line += 1
        
        return records
    
    async def close(self) -> None:
        """Close file."""
        if self._file:
            self._file.close()
            self._file = None
    
    async def get_total_count(self) -> int:
        """Get total count by counting lines."""
        if self._file:
            current = self._file.tell()
            self._file.seek(0)
            count = sum(1 for _ in self._file)
            self._file.seek(current)
            return count
        return 0
    
    def get_checkpoint(self) -> dict:
        """Get current line number."""
        return {"current_line": self._current_line}
    
    def restore_from_checkpoint(self, checkpoint: dict) -> None:
        """Restore from checkpoint."""
        self._current_line = checkpoint.get("current_line", 0)
        if self._file:
            self._file.seek(0)
            for _ in range(self._current_line):
                self._file.readline()
