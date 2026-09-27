"""Megatron `.bin/.idx` export."""

from typing import List, Dict
import struct


class MegatronExporter:
    """Export to Megatron format."""
    
    def __init__(self):
        self._token_map = {}
        self._next_id = 0
    
    def _token_to_id(self, token: str) -> int:
        """Map token to ID."""
        if token not in self._token_map:
            self._token_map[token] = self._next_id
            self._next_id += 1
        return self._token_map[token]
    
    def export(
        self,
        documents: List[Dict],
        output_path: str,
    ) -> Dict:
        """Export documents to Megatron format."""
        # Write .bin file (token IDs)
        bin_path = f"{output_path}.bin"
        with open(bin_path, "wb") as f:
            for doc in documents:
                text = doc.get("text", "")
                tokens = text.split()
                for token in tokens:
                    token_id = self._token_to_id(token)
                    f.write(struct.pack("<I", token_id))
        
        # Write .idx file (index)
        idx_path = f"{output_path}.idx"
        with open(idx_path, "wb") as f:
            offset = 0
            for doc in documents:
                text = doc.get("text", "")
                tokens = text.split()
                num_tokens = len(tokens)
                f.write(struct.pack("<Q", offset))
                f.write(struct.pack("<Q", num_tokens))
                offset += num_tokens * 4
        
        return {
            "bin_path": bin_path,
            "idx_path": idx_path,
            "num_docs": len(documents),
            "vocab_size": len(self._token_map),
        }


def export_to_megatron(documents: List[Dict], output_path: str) -> Dict:
    """Export documents to Megatron format.
    
    Expected: .bin/.idx files created
    """
    exporter = MegatronExporter()
    return exporter.export(documents, output_path)
