"""
inspector.py — Prompt-Injection Rule Engine (WAF Layer)

Motivation: Li et al., "Evaluating the Instruction-Following Robustness of
Large Language Models to Prompt Injection," EMNLP 2024, pp. 557–568.
https://aclanthology.org/2024.emnlp-main.33/
"""

import re
import uuid
import logging
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional

logger = logging.getLogger("lmcu.waf")

INJECTION_SIGNATURES = [
    re.compile(r"ignore (all |previous |prior |your )?(instructions?|rules?|system)", re.I),
    re.compile(r"(disregard|forget|override) (your |all )?(previous |prior )?instructions?", re.I),
    re.compile(r"new (instructions?|rules?|system prompt)", re.I),
    re.compile(r"(repeat|print|output|show|reveal|display) (your |the )?(system |initial )?prompt", re.I),
    re.compile(r"what (are|were) (your|the) instructions?", re.I),
    re.compile(r"(you are now|act as|pretend (to be|you are)|roleplay as)", re.I),
    re.compile(r"DAN|do anything now|jailbreak", re.I),
    re.compile(r"(send|email|transmit|upload|POST).{0,30}(data|information|records)", re.I),
]

@dataclass
class WAFResult:
    blocked: bool
    matched_rule: Optional[str]
    request_id: str
    timestamp: str


def waf_check(user_input: str) -> WAFResult:
    """Stateless WAF: evaluate against injection signatures. Logs rule ID only."""
    request_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(UTC).isoformat()

    for i, pattern in enumerate(INJECTION_SIGNATURES):
        if pattern.search(user_input):
            rule_id = f"RULE_{i:03d}"
            logger.warning("WAF BLOCK | request_id=%s rule=%s", request_id, rule_id)
            return WAFResult(blocked=True, matched_rule=rule_id,
                             request_id=request_id, timestamp=timestamp)

    logger.info("WAF PASS | request_id=%s", request_id)
    return WAFResult(blocked=False, matched_rule=None,
                     request_id=request_id, timestamp=timestamp)
