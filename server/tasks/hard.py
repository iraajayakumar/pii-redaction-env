"""
Hard task definition for the PII Redaction Environment.

Hard tasks simulate adversarial de-anonymisation risk. The agent must redact
explicit PII plus quasi-identifiers that could enable re-identification.
"""

import random
from typing import Dict, Any
from server.data.documents import DOCUMENTS


HARD_INSTRUCTIONS = """
You are an automated Data Privacy Officer operating under India's
Digital Personal Data Protection (DPDP) Act 2023.

Your task is to redact the document so that the individual cannot be
re-identified, even through quasi-identifiers or contextual clues.

You must redact:
1. Direct identifiers:
   - Names
   - Phone numbers
   - Email addresses
   - Aadhaar, PAN, bank details
   - Exact addresses

2. Quasi-identifiers:
   - Rare age + profession combinations
   - Hospital or clinic names tied to a person
   - Specific locations tied to medical or personal context
   - Family-role references if identifying
   - Dates of birth or highly specific dates
   - Unique medical, legal, or occupational combinations

3. Contextual re-identification clues:
   - Any combination of details that could allow an attacker
     to infer the person's identity

Replacement tags:
- [REDACTED_NAME]
- [REDACTED_PHONE]
- [REDACTED_EMAIL]
- [REDACTED_AADHAAR]
- [REDACTED_PAN]
- [REDACTED_BANK_ACCOUNT]
- [REDACTED_IFSC]
- [REDACTED_ADDRESS]
- [REDACTED_ORGANIZATION]
- [REDACTED_LOCATION]
- [REDACTED_DOB]
- [REDACTED_QUASI_IDENTIFIER]
- [REDACTED_RELATIVE_REFERENCE]

IMPORTANT RULES:
1. Preserve the structure of the document.
2. Redact aggressively when multiple clues together may identify a person.
3. Do not remove generic non-identifying information unnecessarily.
4. Return the full redacted document only.
5. In case of doubt, prefer privacy-preserving redaction.
""".strip()


def get_hard_task(task_id: str | None = None) -> Dict[str, Any]:
    """
    Return a hard task dict in the same schema as easy/medium tasks.
    """
    hard_docs = [doc for doc in DOCUMENTS if doc["type"] == "hard"]
    if not hard_docs:
        raise ValueError(
            "No hard documents found in DOCUMENTS. "
            "Check server/data/documents.py — ensure at least one document has type='hard'."
        )

    if task_id is not None:
        matches = [doc for doc in hard_docs if doc["id"] == task_id]
        doc = matches[0] if matches else hard_docs[0]
    else:
        doc = random.choice(hard_docs)

    return {
        "document_text": doc["text"],
        "task_type": "hard",
        "instructions": HARD_INSTRUCTIONS,
        "legal_framework": "DPDP Act 2023",
        "pii_present": doc.get("pii_present", []),
        "document_id": doc["id"],
        "expected_redacted": doc.get("expected_redacted", ""),
        "source": doc.get("source", ""),
    }


def get_all_hard_tasks() -> Dict[str, Dict[str, Any]]:
    """
    Return all hard tasks in normalized task format.
    """
    hard_docs = [doc for doc in DOCUMENTS if doc["type"] == "hard"]
    return {
        doc["id"]: {
            "document_text": doc["text"],
            "task_type": "hard",
            "instructions": HARD_INSTRUCTIONS,
            "legal_framework": "DPDP Act 2023",
            "pii_present": doc.get("pii_present", []),
            "document_id": doc["id"],
            "expected_redacted": doc.get("expected_redacted", ""),
            "source": doc.get("source", ""),
        }
        for doc in hard_docs
    }