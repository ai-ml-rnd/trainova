"""DataTrove operator adapters."""

import re
from typing import Optional

import pyarrow as pa

from services.curation.operators import (
    FilterOperator,
    MapperOperator,
    OpContext,
    register_operator,
)


@register_operator
class LanguageIDFilter(FilterOperator):
    """Language ID filter using fastText."""

    name = "language_id"
    version = "1.0"
    kind = "filter"

    def __init__(self, min_score: float = 0.65, languages: Optional[list[str]] = None):
        self.min_score = min_score
        self.languages = languages or ["en"]

    def filter_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.Table:
        """Filter by language."""
        try:
            import fasttext
        except ImportError:
            raise ImportError("Install fasttext: pip install fasttext")

        # Load model (in production, cache this)
        model = fasttext.load_model("lid.176.bin")

        texts = batch.column(0).to_pylist()
        filtered_rows = []

        for i, text in enumerate(texts):
            prediction = model.predict(text)
            lang, score = prediction[0][0], prediction[1][0]
            lang = lang.replace("__label__", "")

            if score >= self.min_score and lang in self.languages:
                filtered_rows.append(i)

        # Return filtered table
        return batch.take(filtered_rows)


@register_operator
class HeuristicQualityFilter(FilterOperator):
    """Heuristic quality filter based on Gopher/C4/FineWeb patterns."""

    name = "heuristic_quality"
    version = "1.0"
    kind = "filter"

    def __init__(
        self,
        min_words: int = 50,
        max_words_per_line: int = 50,
        min_avg_word_length: float = 3,
        max_avg_word_length: float = 10,
    ):
        self.min_words = min_words
        self.max_words_per_line = max_words_per_line
        self.min_avg_word_length = min_avg_word_length
        self.max_avg_word_length = max_avg_word_length

    def filter_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.Table:
        """Filter by quality heuristics."""
        texts = batch.column(0).to_pylist()
        filtered_rows = []

        for i, text in enumerate(texts):
            lines = text.split("\n")

            # Check words per line
            if any(len(line.split()) > self.max_words_per_line for line in lines):
                continue

            # Check word count
            words = text.split()
            if len(words) < self.min_words:
                continue

            # Check average word length
            word_lengths = [len(w) for w in words if w.strip()]
            if not word_lengths:
                continue

            avg_length = sum(word_lengths) / len(word_lengths)
            if not (self.min_avg_word_length <= avg_length <= self.max_avg_word_length):
                continue

            filtered_rows.append(i)

        return batch.take(filtered_rows)


@register_operator
class PIIRegexFilter(FilterOperator):
    """PII detection using regex patterns."""

    name = "pii_regex"
    version = "1.0"
    kind = "filter"

    PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "url": r"https?://\S+",
    }

    def filter_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.Table:
        """Filter rows containing PII patterns."""
        texts = batch.column(0).to_pylist()
        filtered_rows = []

        for i, text in enumerate(texts):
            has_pii = False
            for pattern in self.PATTERNS.values():
                if re.search(pattern, text):
                    has_pii = True
                    break

            if not has_pii:
                filtered_rows.append(i)

        return batch.take(filtered_rows)


@register_operator
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
            from transformers import AutoTokenizer

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
