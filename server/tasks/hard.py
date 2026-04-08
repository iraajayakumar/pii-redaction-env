"""
HARD TASK: De-anonymisation Attack & Defense
=============================================

Objective: Can an adversary re-identify a person from a redacted document using quasi-identifiers?

The Challenge:
--------------
1. An agent receives a redacted document where explicit PII (Aadhaar, PAN, phone) has been removed
2. The agent must identify if the document is still vulnerable to re-identification
3. The agent acts as both editor and attacker:
   - First, it checks: "Can someone identify this person using remaining information?"
   - If yes, the agent must re-redact more aggressively
   - This repeats up to 3 times until either:
     a) Re-identification fails (SUCCESS)
     b) Max attempts reached (FAILURE)

Quasi-Identifiers:
------------------
Quasi-identifiers are seemingly harmless attributes that, when combined, can uniquely identify
an individual. Examples:

✗ NOT re-identifiable alone:
  - "Software Engineer" (too common)
  - "Age 34" (too common)
  - "Lives in Delhi" (too common)

✓ RE-IDENTIFIABLE TOGETHER:
  - "34-year-old female cardiologist with Takayasu's arteritis at AIIMS Delhi, lives in Lajpat Nagar"
    → Combination is rare enough to identify

Scoring:
--------
The grader scores on two factors:
1. Medium baseline (0-1): How good is the initial redaction?
2. Adversarial defense (0-1): How quickly did agent defend against re-identification?

Final Score = 0.5 × medium_baseline + 0.5 × (max_attempts - actual_attempts) / max_attempts
"""

# Import professional hard task documents from documents.py
# Using late import to avoid circular dependencies
_HARD_SAMPLES = None

def _get_hard_samples():
    """Lazy-load hard task samples from documents."""
    global _HARD_SAMPLES
    if _HARD_SAMPLES is None:
        from server.data.documents import DOCUMENTS
        _HARD_SAMPLES = {
            doc["id"]: {
                "id": doc["id"],
                "text": doc["text"],
                "pii_present": doc.get("pii_present", []),
                "expected_redacted": doc.get("expected_redacted", ""),
                "source": doc.get("source", "")
            }
            for doc in DOCUMENTS
            if doc["type"] == "hard"
        }
    return _HARD_SAMPLES

# Provide access to samples through a dict-like interface
class _HardTaskSamplesProxy:
    def __getitem__(self, key):
        return _get_hard_samples()[key]
    
    def __contains__(self, key):
        return key in _get_hard_samples()
    
    def values(self):
        return _get_hard_samples().values()
    
    def keys(self):
        return _get_hard_samples().keys()
    
    def get(self, key, default=None):
        return _get_hard_samples().get(key, default)

HARD_TASK_SAMPLES = _HardTaskSamplesProxy()


def get_hard_task(task_id: str = "hard_021") -> dict:
    """
    Get a specific hard task sample.
    
    Args:
        task_id: Task ID (hard_021 through hard_030)
    
    Returns:
        Dictionary with id, text, pii_present, expected_redacted, source
    """
    if task_id not in HARD_TASK_SAMPLES:
        task_id = "hard_021"  # Default to first hard task
    
    return HARD_TASK_SAMPLES[task_id]


def get_all_hard_tasks() -> dict:
    """Get all hard task samples."""
    return HARD_TASK_SAMPLES