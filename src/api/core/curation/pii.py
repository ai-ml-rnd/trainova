"""PII detection and redaction operators."""

from typing import List, Dict, Optional
import re

from core.curation.operator import TaggerOperator, OperatorKind, OpContext
import pyarrow as pa


class PIIDetector(TaggerOperator):
    """PII detection using Presidio-style regex patterns."""
    
    name: str = "pii_detector"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.TAGGER
    
    def __init__(self, redaction_mode: str = "tag"):
        """
        Args:
            redaction_mode: one of 'tag', 'hash', 'replace', 'redact'
        """
        self.redaction_mode = redaction_mode
        
        # Common regex patterns for PII
        self.patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "us_ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        }
    
    def detect(self, text: str) -> List[Dict]:
        """Detect PII in text."""
        findings = []
        
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                findings.append({
                    "type": pii_type,
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(),
                })
        
        return findings
    
    def redact(self, text: str, findings: List[Dict]) -> str:
        """Apply redaction to text."""
        if not findings:
            return text
        
        if self.redaction_mode == "redact":
            # Replace with [REDACTED]
            result = text
            for finding in sorted(findings, key=lambda x: x["start"], reverse=True):
                result = (
                    result[:finding["start"]] +
                    "[REDACTED]" +
                    result[finding["end"]:]
                )
            return result
        
        elif self.redaction_mode == "hash":
            # Replace with hash
            result = text
            for finding in sorted(findings, key=lambda x: x["start"], reverse=True):
                hash_val = hash(finding["text"])
                result = (
                    result[:finding["start"]] +
                    f"[HASH:{hash_val}]" +
                    result[finding["end"]:]
                )
            return result
        
        elif self.redaction_mode == "tag":
            # Keep original, just tag
            return text
        
        else:  # replace with type
            result = text
            for finding in sorted(findings, key=lambda x: x["start"], reverse=True):
                result = (
                    result[:finding["start"]] +
                    f"[{finding['type'].upper()}]" +
                    result[finding["end"]:]
                )
            return result
    
    def tag(self, batch: pa.RecordBatch) -> dict:
        """Tag batch with PII findings."""
        if "text" not in batch.column_names:
            return {}
        
        texts = batch.column("text").to_pylist()
        
        pii_flags = []
        pii_redacted_text = []
        
        for text in texts:
            if not text:
                pii_flags.append([])
                pii_redacted_text.append("")
                continue
            
            findings = self.detect(text)
            pii_flags.append([f["type"] for f in findings])
            
            if self.redaction_mode == "redact":
                pii_redacted_text.append(self.redact(text, findings))
            else:
                pii_redacted_text.append(text)
        
        return {
            "pii_flags": pii_flags,
            "pii_redacted_text": pii_redacted_text,
        }


def register_pii_operators(registry):
    """Register PII operators."""
    registry.register(PIIDetector())
    registry.register(PIIDetector(redaction_mode="redact"))
    registry.register(PIIDetector(redaction_mode="hash"))
