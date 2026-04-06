"""
Easy task definition for the PII Redaction Environment.
Easy tasks contain only structured, directly detectable PII:
Aadhaar, PAN, phone, email, bank account, IFSC.
"""

import random
from typing import Dict, Any
from server.data.documents import DOCUMENTS

EASY_INSTRUCTIONS = """
You are an automated Data Privacy Officer operating under India's 
Digital Personal Data Protection (DPDP) Act 2023.

Your task is to redact ALL structured PII from the document below.

PII types to redact and their formats:
- Aadhaar numbers: 12-digit numbers, formatted as XXXX XXXX XXXX or XXXXXXXXXXXX
- PAN card numbers: format ABCDE1234F (5 letters + 4 digits + 1 letter, all caps)
- Indian phone numbers: starting with +91 followed by 10 digits, OR standalone 10-digit numbers starting with 6, 7, 8, or 9
- Email addresses: any valid email format
- Bank account numbers: 9 to 18 digit numeric strings
- IFSC codes: format ABCD0XXXXXX (4 letters + 0 + 6 alphanumeric)

Replacement format — use these exact tags:
- [REDACTED_AADHAAR]
- [REDACTED_PAN]
- [REDACTED_PHONE]
- [REDACTED_EMAIL]
- [REDACTED_BANK_ACCOUNT]
- [REDACTED_IFSC]

IMPORTANT RULES:
1. Replace PII with the tag — do NOT delete it entirely
2. Do NOT redact non-PII numbers (dates, amounts, order IDs, pin codes)
3. Do NOT redact organisation names, doctor names, or place names
4. Return the complete document with only PII replaced
5. If you are unsure whether something is PII, err on the side of redacting it
""".strip()

def get_easy_task() -> Dict[str, Any]:
    """
    Samples a random easy document and returns a task dict.
    Called by the environment's reset() method.
    
    Returns:
        Dict containing document_text, task_type, instructions,
        legal_framework, pii_present, and document_id.
    """
    easy_docs = [doc for doc in DOCUMENTS if doc["type"] == "easy"]
    if not easy_docs:
        raise ValueError(
            "No easy documents found in DOCUMENTS. "
            "Check server/data/documents.py — ensure at least one document has type='easy'."
        )
    doc = random.choice(easy_docs)
    return {
        "document_text": doc["text"],
        "task_type": "easy",
        "instructions": EASY_INSTRUCTIONS,
        "legal_framework": "DPDP Act 2023",
        "pii_present": doc["pii_present"],
        "document_id": doc["id"],
        "expected_redacted": doc.get("expected_redacted", ""),
    }