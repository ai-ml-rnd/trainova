"""PII detection and redaction service."""

import re
from typing import Optional

import pyarrow as pa

from services.curation.operators import MapperOperator, OpContext


class PIIDetector:
    """PII detection using Presidio + regex."""

    PATTERN_EMAIL = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    PATTERN_PHONE = r"\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    PATTERN_IP = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    PATTERN_URL = r"https?://\S+"
    PATTERN_CREDIT_CARD = r"\b(?:\d{4}[-.\s]?){3}\d{4}\b"
    PATTERN_SSN = r"\b\d{3}-\d{2}-\d{4}\b"

    PATTERNS = {
        "email": PATTERN_EMAIL,
        "phone": PATTERN_PHONE,
        "ip": PATTERN_IP,
        "url": PATTERN_URL,
        "credit_card": PATTERN_CREDIT_CARD,
        "ssn": PATTERN_SSN,
    }

    def __init__(self, detect_all: bool = True, redact: bool = False):
        self.detect_all = detect_all
        self.redact = redact

    def detect(self, text: str) -> list[dict]:
        """Detect PII in text."""
        findings = []

        for pii_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text):
                findings.append({
                    "type": pii_type,
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(),
                })

        return findings

    def redact_text(self, text: str) -> str:
        """Redact PII from text."""
        result = text
        for pii_type, pattern in self.PATTERNS.items():
            result = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", result)
        return result


class PIIOperator(MapperOperator):
    """PII detection and redaction operator."""

    name = "pii"
    version = "1.0"
    kind = "mapper"

    def __init__(self, redact: bool = True):
        self.detector = PIIDetector(detect_all=True, redact=redact)
        self.redact = redact

    def process_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.RecordBatch:
        """Process batch to detect and redact PII."""
        texts = batch.column(0).to_pylist()

        pii_flags = []
        redacted_texts = []

        for text in texts:
            findings = self.detector.detect(text)

            if self.redact:
                redacted_texts.append(self.detector.redact_text(text))
            else:
                redacted_texts.append(text)

            pii_flags.append({
                "pii_count": len(findings),
                "pii_types": list(set(f["type"] for f in findings)),
                "findings": findings,
            })

        # Add new columns
        new_columns = list(batch.columns)
        new_columns.append(pa.array(pii_flags, type=pa.string()))
        new_columns.append(pa.array(redacted_texts, type=pa.string()))

        new_names = list(batch.schema.names)
        new_names.extend(["pii_flags", "text_redacted"])

        return pa.RecordBatch.from_arrays(new_columns, schema=pa.schema(new_names))


async def run_pii_scan(dataset_id: str, redact: bool = True) -> dict:
    """Run PII scan on a dataset."""
    detector = PIIDetector(detect_all=True, redact=redact)

    # TODO: Load records from Lance
    # records = ...

    results = []
    for record in []:  # TODO: iterate over records
        findings = detector.detect(record.get("text", ""))
        results.append({
            "record_id": record.get("record_id"),
            "pii_count": len(findings),
            "pii_types": list(set(f["type"] for f in findings)),
        })

    return {
        "dataset_id": dataset_id,
        "pii_scan_results": results,
        "total_records_scanned": len(results),
        "records_with_pii": sum(1 for r in results if r["pii_count"] > 0),
        "redact": redact,
    }
