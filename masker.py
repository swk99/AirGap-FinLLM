"""
masker.py — PII Detection & Token Substitution
"""

import re
import hashlib
from dataclasses import dataclass

PII_PATTERNS = {
    "ACCOUNT_NUMBER": re.compile(r"\b\d{8,12}\b"),
    "SORT_CODE":      re.compile(r"\b\d{2}-\d{2}-\d{2}\b"),
    "POSTCODE":       re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", re.I),
    "EMAIL":          re.compile(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", re.I),
    "PHONE":          re.compile(r"\b(?:\+44|0)[\d\s\-]{9,13}\b"),
    "NI_NUMBER":      re.compile(r"\b[A-Z]{2}\d{6}[A-D]\b", re.I),
    "FULL_NAME":      re.compile(
        r"\b(Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+([\s-][A-Z][a-z]+)+\b"
    ),
}

@dataclass
class MaskingResult:
    masked_text: str
    redaction_map: dict   # token → original (in-memory only, never persisted)
    pii_found: list


def mask_pii(text: str) -> MaskingResult:
    """Replace PII with deterministic tokens before LLM ingestion."""
    redaction_map = {}
    pii_found = []

    for label, pattern in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if not matches:
            continue
        flat = (matches if isinstance(matches[0], str)
                else [m if isinstance(m, str) else m[0] for m in matches])
        for match in set(flat):
            token = f"[{label}_{hashlib.sha256(match.encode()).hexdigest()[:6].upper()}]"
            redaction_map[token] = match
            text = text.replace(match, token)
            pii_found.append(label)

    return MaskingResult(
        masked_text=text,
        redaction_map=redaction_map,
        pii_found=list(set(pii_found)),
    )
