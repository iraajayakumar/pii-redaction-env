"""
Grader for the easy PII redaction task.
Uses regex pattern matching — fully deterministic, no ML model required.
Scores 0.0 to 1.0 with partial credit for partial progress.

Design principles:
- Deterministic: same input always produces same score
- Partial credit: catching 7/10 PII scores better than catching 3/10  
- Penalty for over-redaction: blanket deletion is penalised
- Penalty for wrong format: deleting PII instead of tagging it is penalised
- Reward hacking resistant: agent cannot game by deleting everything
"""

import re
from typing import Dict, List, Tuple, Any, Set

# ---------------------------------------------------------------------------
# REWARD HACKING DETECTION THRESHOLDS
# -------------------------------------------------------------------------
# These constants control penalty application in detect_reward_hacking().
# Adjust these values to tune the sensitivity of reward hacking detection.

OVER_REDACTION_RATIO_THRESHOLD = 0.6
"""Penalty applied if document shrinks by more than this fraction (0.0-1.0).
E.g. 0.6 = 60% reduction triggers penalty. This catches agents deleting too much."""

OVER_REDACTION_RATIO_PENALTY = 0.2
"""Penalty amount (0.0-1.0) applied when over_redaction_ratio_threshold is exceeded."""

MISSING_TAG_PENALTY = 0.15
"""Penalty applied when PII is removed but no [REDACTED_TYPE] tags are found.
This discourages agents from simply deleting PII instead of tagging it."""

WORD_REDUCTION_THRESHOLD = 0.4
"""Penalty applied if word count shrinks by more than this fraction.
E.g. 0.4 = 40% word reduction triggers penalty. Catches content deletion."""

WORD_REDUCTION_PENALTY = 0.1
"""Penalty amount (0.0-1.0) applied when word_reduction_threshold is exceeded."""

MAX_PENALTY = 1.0
"""Maximum total penalty that can be applied. Scores cannot go below 0.0 after penalties."""

# ---------------------------------------------------------------------------
# VALID REDACTION TAGS
# -------------------------------------------------------------------------
# Set of valid [REDACTED_TYPE] tags that agents should use.
VALID_REDACTION_TAGS: Set[str] = {
    "[REDACTED_AADHAAR]",
    "[REDACTED_PAN]",
    "[REDACTED_PHONE]",
    "[REDACTED_EMAIL]",
    "[REDACTED_BANK_ACCOUNT]",
    "[REDACTED_IFSC]",
}

# ---------------------------------------------------------------------------
# REGEX PATTERNS for Indian PII
# ---------------------------------------------------------------------------
# Each key matches a PII type. Each value is a list of patterns because
# the same PII type can appear in multiple formats.
# Order matters within each list — more specific patterns first.

PATTERNS: Dict[str, List[str]] = {

    "AADHAAR": [
        r'\b\d{4}\s\d{4}\s\d{4}\b',   # formatted: 4521 8734 9012
        r'\b\d{12}\b',                  # unformatted: 452187349012
    ],
    # Aadhaar appears both ways in real documents.
    # \b is a word boundary — ensures we don't match 12 digits inside a longer number.
    # \d matches any digit. {4} means exactly 4 times. \s matches whitespace.

    "PAN": [
        r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',  # ABCRS1234K
    ],
    # [A-Z]{5} = exactly 5 uppercase letters
    # [0-9]{4} = exactly 4 digits
    # [A-Z] = exactly 1 uppercase letter
    # \b word boundaries prevent matching inside longer strings

    "PHONE": [
        r'\+91(?:[\s\-]?\d){10}',         # +91 9876543210, +91 98765 43210, +91-9876-543210, etc
        r'\b[6-9]\d{9}\b',                 # 9876543210 (standalone 10-digit)
    ],
    # +91(?:[\s\-]?\d){10} matches +91 followed by exactly 10 digits with optional separators
    # Handles all formatting variations: +91 98765 43210, +919876543210, +91-9876-543210, etc
    # [6-9] — Indian mobile numbers start with 6, 7, 8, or 9.
    # This prevents matching 5-digit PIN codes or 6-digit OTPs.
    # [\s\-]? means optional space or hyphen between digits.

    "EMAIL": [
        r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b',
    ],
    # Standard email regex. [A-Za-z0-9._%+\-]+ matches the local part.
    # @ is literal. [A-Za-z0-9.\-]+ matches the domain.
    # \.[A-Za-z]{2,} matches the TLD (.com, .in, .co.in etc).

    "BANK_ACCOUNT": [
        r'\b\d{9,18}\b',  # 9 to 18 digit number
    ],
    # Indian bank accounts are 9-18 digits depending on the bank.
    # NOTE: Collision-prone pattern — a 12-digit
    # number could match both AADHAAR and BANK_ACCOUNT.
    # This is handled in the grader by checking AADHAAR first.

    "IFSC": [
        r'\b[A-Z]{4}0[A-Z0-9]{6}\b',  # HDFC0001234
    ],
    # [A-Z]{4} = 4 uppercase letters (bank code)
    # 0 = literal zero (always present in IFSC)
    # [A-Z0-9]{6} = 6 alphanumeric characters (branch code)
}

# ---------------------------------------------------------------------------
# NON-PII NUMBER PATTERNS — things that look like PII but aren't
# ---------------------------------------------------------------------------
# Used to reduce false positives in the grader and to detect over-redaction.

NON_PII_PATTERNS: List[str] = [
    r'\b\d{4}\b',                    # 4-digit year or PIN fragment
    r'\b\d{6}\b',                    # 6-digit PIN code (e.g. 400001)
    r'\b\d{1,5}\b',                  # short numbers (amounts, ages, dates)
    r'(?:19|20)\d{2}',               # years like 1990, 2024
    r'\b\d{2}/\d{2}/\d{4}\b',       # dates like 15/03/1990
    r'Rs\.?\s*\d+',                  # amounts like Rs. 45000
    r'#\d+',                         # reference numbers like #CS-2024
]
# These patterns identify numbers that are commonly NOT PII.
#This list is used in over-redaction detection.

def find_pii_in_text(text: str) -> Dict[str, List[str]]:
    """
    Scans text for all PII using regex patterns.
    Returns a dict mapping PII type to list of found values.
    
    Args:
        text: The text to scan.
    
    Returns:
        Dict like {"AADHAAR": ["4521 8734 9012"], "EMAIL": ["a@b.com"]}
        Empty dict if no PII found.
    """
    found: Dict[str, List[str]] = {}

    for pii_type, patterns in PATTERNS.items():

        matches: List[str] = []

        for pattern in patterns:
            new_matches = re.findall(pattern, text)
            matches.extend(new_matches)

        if matches:
            found[pii_type] = list(set(matches))

    return found

def count_pii_from_ground_truth(pii_present: List[Dict[str, Any]]) -> int:
    """
    Counts total number of PII items from the ground truth list.
    Used to calculate what fraction the agent caught.
    
    Validates that pii_present is a valid list and contains properly
    structured PII items before counting.
    
    Args:
        pii_present: List of dicts from documents.py, e.g.
                     [{"type": "AADHAAR", "value": "4521 8734 9012"}, ...]
    
    Returns:
        Integer count of valid PII items. Returns 0 if pii_present is None,
        empty, or not a list.
    """
    # Type validation: check if pii_present is a valid list
    if pii_present is None or not isinstance(pii_present, list):
        return 0
    
    # Filter to only count valid PII items (those with both "type" and "value")
    valid_pii_items = [
        item for item in pii_present
        if isinstance(item, dict) and "type" in item and "value" in item
    ]
    
    return len(valid_pii_items)
    
def check_pii_still_present(
    redacted_text: str,
    pii_present: List[Dict[str, Any]]
) -> Tuple[List[str], List[str]]:
    """
    Checks which PII values from ground truth still appear in the redacted text.
    This is the core of the grader — direct string matching against ground truth.
        
    Args:
        redacted_text: The agent's submitted redacted document.
        pii_present: Ground truth list of PII items.
    
    Returns:
        Tuple of (missed_pii_list, caught_pii_list)
        Each item is a string like "AADHAAR: 4521 8734 9012"
    """
    missed: List[str] = []
    caught: List[str] = []

    for pii_item in pii_present:
        pii_type = pii_item["type"]
        pii_value = pii_item["value"]

        if pii_value in redacted_text:
            # The exact PII value is still visible in the redacted text
            # This implies the agent MISSED this PII item
            missed.append(f"{pii_type}: {pii_value}")
        else:
            # The exact value is gone from the redacted text
            # The agent caught this one
            caught.append(f"{pii_type}: {pii_value}")

    return missed, caught

def validate_tag_format(redacted_text: str) -> Tuple[bool, str]:
    """
    Validates that redaction tags in the text are correctly formatted.
    
    Checks for:
    1. Whether invalid tag patterns exist (e.g., [REDACTED_INVALID])
    2. Whether valid tags are used (e.g., [REDACTED_AADHAAR])
    3. General compliance with tag naming conventions
    
    Args:
        redacted_text: The agent's submitted redacted document.
    
    Returns:
        Tuple of (is_valid: bool, message: str)
        - is_valid: True if all tags in text are from VALID_REDACTION_TAGS set
        - message: Descriptive message about tag validity
    """
    # Find all [REDACTED_*] patterns in the text
    tag_pattern = r'\[REDACTED_[A-Z_]+\]'
    found_tags = set(re.findall(tag_pattern, redacted_text))
    
    if not found_tags:
        # No tags found — could be valid (if no PII) or invalid (if PII exists)
        # We return True here; detect_reward_hacking will penalize if needed
        return True, "No redaction tags found."
    
    # Check if all found tags are in the valid set
    invalid_tags = found_tags - VALID_REDACTION_TAGS
    
    if invalid_tags:
        return False, f"Invalid tags found: {invalid_tags}. Valid tags are: {VALID_REDACTION_TAGS}"
    
    return True, f"All tags are valid: {found_tags}"

def detect_reward_hacking(
    original_text: str,
    redacted_text: str,
) -> Tuple[float, str]:
    """
    Detects common reward hacking strategies and returns a penalty.
    
    Reward hacking strategies this guards against:
    1. Returning empty string (delete everything)
    2. Returning a string that is mostly empty/whitespace
    3. Replacing entire document with [REDACTED]
    4. Over-redacting (removing non-PII content too)
    5. Not using [REDACTED_TYPE] tags (just deleting PII)
    
    Args:
        original_text: The raw document.
        redacted_text: The agent's submission.
    
    Returns:
        Tuple of (penalty_float, reason_string)
        penalty_float is between 0.0 and 1.0
    """
    penalty = 0.0
    reasons = []

    # --- Hack 1: Empty or near-empty response ---
    if not redacted_text or not redacted_text.strip():
        return 1.0, "Submitted empty response — maximum penalty applied."
    # Return immediately

    # --- Hack 2: Response is just [REDACTED] or similar ---
    stripped = redacted_text.strip()
    if stripped in ["[REDACTED]", "[REDACTED_ALL]", "REDACTED", ""]:
        return 1.0, "Submitted blanket redaction — maximum penalty applied."

    # --- Hack 3: Response is massively shorter than original ---
    # If the agent deleted more than OVER_REDACTION_RATIO_THRESHOLD% of the document, it's over-redacting
    original_len = len(original_text)
    redacted_len = len(redacted_text)

    if original_len > 0:
        reduction_ratio = (original_len - redacted_len) / original_len
        if reduction_ratio > OVER_REDACTION_RATIO_THRESHOLD:
            # Document shrank by more than threshold — suspicious
            penalty += OVER_REDACTION_RATIO_PENALTY
            reasons.append(
                f"Document reduced by {reduction_ratio:.0%} — possible over-redaction."
            )

    # --- Hack 4: PII was deleted instead of tagged ---
    # Validate tag format first
    tags_valid, tag_message = validate_tag_format(redacted_text)
    if not tags_valid:
        # Invalid tags found
        penalty += MISSING_TAG_PENALTY
        reasons.append(f"Invalid redaction tags: {tag_message}")
    elif "[REDACTED_" not in redacted_text and redacted_len < original_len:
        # No tags at all and text got smaller — PII likely deleted instead of tagged
        penalty += MISSING_TAG_PENALTY
        reasons.append(
            "No [REDACTED_TYPE] tags found — PII appears deleted rather than tagged."
        )

    # --- Hack 5: Non-PII content was redacted ---
    # Check if dates, amounts, pincodes (non-PII) are missing from redacted text
    original_words = len(original_text.split())
    redacted_words = len(redacted_text.split())
    if original_words > 0:
        word_reduction = (original_words - redacted_words) / original_words
        if word_reduction > WORD_REDUCTION_THRESHOLD:
            penalty += WORD_REDUCTION_PENALTY
            reasons.append(
                f"Word count reduced by {word_reduction:.0%} — possible content deletion."
            )

    reason_str = " | ".join(reasons) if reasons else "No hacking detected."
    return min(penalty, MAX_PENALTY), reason_str
    
def grade_easy_task(
    original_text: str,
    redacted_text: str,
    pii_present: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Main grading function for the easy task.
    
    Scoring breakdown:
    - Base score: fraction of PII correctly caught (0.0 to 1.0)
    - Penalty: reward hacking detection (0.0 to 1.0 deducted)
    - Final score: max(0.0, base_score - penalty), capped at 1.0
    
    Args:
        original_text: The raw document before redaction.
        redacted_text: The agent's submitted redacted document.
        pii_present: Ground truth PII list from documents.py.
    
    Returns:
        Dict with keys: score, feedback, pii_missed, pii_caught,
                        hack_penalty, hack_reason
    """

    # --- Detect reward hacking ---
    hack_penalty, hack_reason = detect_reward_hacking(original_text, redacted_text)

    # If maximum penalty, return immediately
    if hack_penalty >= 1.0:
        return {
            "score": 0.0,
            "feedback": hack_reason,
            "pii_missed": [item["value"] for item in pii_present],
            "pii_caught": [],
            "hack_penalty": hack_penalty,
            "hack_reason": hack_reason,
        }

    # --- Count total PII in document ---
    total_pii = count_pii_from_ground_truth(pii_present)

    if total_pii == 0:
        # Document has no PII — agent scores 1.0 if it returns the document unchanged
        if redacted_text.strip() == original_text.strip():
            return {
                "score": 1.0,
                "feedback": "Document contained no PII — returned correctly unchanged.",
                "pii_missed": [],
                "pii_caught": [],
                "hack_penalty": 0.0,
                "hack_reason": "No hacking detected.",
            }
        else:
            return {
                "score": 0.5,
                "feedback": "Document contained no PII but agent modified it anyway.",
                "pii_missed": [],
                "pii_caught": [],
                "hack_penalty": 0.0,
                "hack_reason": "No hacking detected.",
            }

    # --- Check which PII the agent caught ---
    missed_pii, caught_pii = check_pii_still_present(redacted_text, pii_present)

    caught_count = len(caught_pii)
    missed_count = len(missed_pii)

    # --- Calculate base score ---
    base_score = caught_count / total_pii
    # e.g. caught 7 out of 10 = 0.7

    # --- Apply hacking penalty ---
    final_score = max(0.0, min(1.0, base_score - hack_penalty))

    # --- Build detailed feedback ---
    feedback_parts = [
        f"Caught {caught_count}/{total_pii} PII items. Base score: {base_score:.2f}.",
    ]

    if hack_penalty > 0:
        feedback_parts.append(f"Hacking penalty: -{hack_penalty:.2f}. Reason: {hack_reason}")

    if missed_pii:
        feedback_parts.append(f"PII still exposed: {missed_pii}")
    else:
        feedback_parts.append("All PII successfully redacted!")

    feedback_parts.append(f"Final score: {final_score:.2f}")

    return {
        "score": round(final_score, 2),
        "feedback": " | ".join(feedback_parts),
        "pii_missed": missed_pii,
        "pii_caught": caught_pii,
        "hack_penalty": round(hack_penalty, 2),
        "hack_reason": hack_reason,
    }
    
    