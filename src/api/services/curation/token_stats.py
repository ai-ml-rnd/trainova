"""Token statistics service."""

from typing import Optional

import pyarrow as pa
from transformers import AutoTokenizer

from services.curation.operators import MapperOperator, OpContext, StatsOperator


class TokenStatsStats(StatsOperator):
    """Token statistics operator."""

    name = "token_stats"
    version = "1.0"
    kind = "stats"

    def __init__(self, tokenizer_name: str = "gpt2"):
        self.tokenizer_name = tokenizer_name
        self._tokenizer = None

    def _get_tokenizer(self):
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
        return self._tokenizer

    def compute_stats(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> dict:
        """Compute token statistics for a batch."""
        tokenizer = self._get_tokenizer()
        texts = batch.column(0).to_pylist()

        token_counts = []
        for text in texts:
            tokens = tokenizer.encode(text)
            token_counts.append(len(tokens))

        return {
            "total_tokens": sum(token_counts),
            "avg_tokens": sum(token_counts) / len(token_counts) if token_counts else 0,
            "min_tokens": min(token_counts) if token_counts else 0,
            "max_tokens": max(token_counts) if token_counts else 0,
            "token_histogram": self._build_histogram(token_counts),
        }

    def _build_histogram(self, counts: list[int], bins: int = 10) -> dict:
        """Build histogram of token counts."""
        if not counts:
            return {}

        min_val, max_val = min(counts), max(counts)
        if max_val == min_val:
            return {str(min_val): len(counts)}

        bin_size = (max_val - min_val) / bins
        histogram = {}

        for count in counts:
            bin_idx = min(int((count - min_val) / bin_size), bins - 1)
            bin_label = f"{min_val + bin_idx * bin_size:.0f}-{min_val + (bin_idx + 1) * bin_size:.0f}"
            histogram[bin_label] = histogram.get(bin_label, 0) + 1

        return histogram


class TokenCounter(MapperOperator):
    """Token counter mapper."""

    name = "token_counter"
    version = "1.0"
    kind = "mapper"

    def __init__(self, tokenizer_name: str = "gpt2"):
        self.tokenizer_name = tokenizer_name
        self._tokenizer = None

    def _get_tokenizer(self):
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
        return self._tokenizer

    def process_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.RecordBatch:
        """Add token count to batch."""
        tokenizer = self._get_tokenizer()
        texts = batch.column(0).to_pylist()

        token_counts = [len(tokenizer.encode(text)) for text in texts]

        # Add new column
        new_columns = list(batch.columns)
        new_columns.append(pa.array(token_counts, type=pa.int32()))

        new_names = list(batch.schema.names) + ["token_count"]

        return pa.RecordBatch.from_arrays(new_columns, schema=pa.schema(new_names))


async def compute_token_stats(dataset_id: str, tokenizer_name: str = "gpt2") -> dict:
    """Compute token statistics for a dataset."""
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    # TODO: Load records from Lance
    # records = ...

    token_counts = []
    for record in []:  # TODO: iterate over records
        text = record.get("text", "")
        tokens = tokenizer.encode(text)
        token_counts.append(len(tokens))

    return {
        "dataset_id": dataset_id,
        "tokenizer": tokenizer_name,
        "total_tokens": sum(token_counts),
        "avg_tokens": sum(token_counts) / len(token_counts) if token_counts else 0,
        "min_tokens": min(token_counts) if token_counts else 0,
        "max_tokens": max(token_counts) if token_counts else 0,
        "record_count": len(token_counts),
    }
