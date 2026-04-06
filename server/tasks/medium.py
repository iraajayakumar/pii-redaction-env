"""
Medium task definition for the PII Redaction Environment.
Medium tasks contain contextual/implicit PII that requires NER + LLM understanding:
- Doctor/healthcare provider names
- Hospital/clinic names  
- Patient names (inferred from context like "the patient's wife [NAME]")
- Relative references (indirect identifiers: "my cousin", "the treating physician", etc.)
- Derived attributes that enable re-identification
"""

import random
from typing import Dict, Any
from server.data.documents import DOCUMENTS

MEDIUM_INSTRUCTIONS = """
You are an automated Data Privacy Officer operating under India's 
Digital Personal Data Protection (DPDP) Act 2023.

Your task is to redact ALL PII from the document below — including both
EXPLICIT and CONTEXTUAL PII that could enable re-identification.

PII types to redact:
1. DIRECT IDENTIFIERS (explicit in text):
   - Patient name
   - Doctor/physician name
   - Healthcare provider name
   - Hospital/clinic name
   - Address

2. CONTEXTUAL IDENTIFIERS (inferred from context):
   - Relative references: "the patient's wife", "his treating physician", "met with the cardiologist"
   - Disease + location combinations that could re-identify
   - Rare demographic combinations

3. QUASI-IDENTIFIERS (indirect identifiers):
   - Date of birth, DOB
   - Phone numbers
   - Email addresses

Replacement format — use exact tags matching the PII type:
- [REDACTED_NAME] — for person names (patient, doctor, family)
- [REDACTED_ORGANIZATION] — for hospital/clinic names
- [REDACTED_ADDRESS] — for addresses
- [REDACTED_PHONE] — for phone numbers
- [REDACTED_EMAIL] — for email addresses
- [REDACTED_DOB] — for dates of birth
- [REDACTED_RELATIVE_REFERENCE] — for "his wife", "my cousin", etc. (use generic reference if needed)

IMPORTANT RULES:
1. Replace PII with the appropriate tag — do NOT delete it entirely
2. Preserve document structure and readability
3. If a reference identifies a person contextually (e.g., "the patient's wife Sarah"), mark it for redaction
4. Do NOT redact medical conditions (e.g., "Type 2 Diabetes" is NOT PII by itself)
5. Do NOT redact generic organisation mentions if they don't identify a specific person
6. When in doubt, err on the side of redacting — privacy is paramount
7. Return the complete document with all PII replaced

EXAMPLE:
Original: "Dr. Anand Krishnamurthy treated Suresh Iyer on 22/07/1968."
Redacted: "[REDACTED_NAME] treated [REDACTED_NAME] on [REDACTED_DOB]."
""".strip()


def get_medium_task() -> Dict[str, Any]:
    """
    Samples a random medium document and returns a task dict.
    Called by the environment's reset() method.
    
    Medium tasks include contextual/implicit PII that requires NER + LLM understanding.
    
    Returns:
        Dict containing document_text, task_type, instructions,
        legal_framework, pii_present, and document_id.
    """
    medium_docs = [doc for doc in DOCUMENTS if doc["type"] == "medium"]
    if not medium_docs:
        raise ValueError(
            "No medium documents found in DOCUMENTS. "
            "Check server/data/documents.py — ensure at least one document has type='medium'."
        )
    doc = random.choice(medium_docs)
    return {
        "document_text": doc["text"],
        "task_type": "medium",
        "instructions": MEDIUM_INSTRUCTIONS,
        "legal_framework": "DPDP Act 2023",
        "pii_present": doc["pii_present"],
        "document_id": doc["id"],
        "expected_redacted": doc.get("expected_redacted", ""),
    }