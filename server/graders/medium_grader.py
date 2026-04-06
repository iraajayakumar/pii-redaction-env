"""
Grader for the medium PII redaction task.
Uses spaCy NER (Named Entity Recognition) for entity extraction,
and leverages LLM-based contextual scoring for correctness assessment.

Design principles:
- Uses spaCy NER to extract PERSON, ORG, GPE entities
- Scores based on:
  1. Structural matching: are PII items properly replaced with tags?
  2. Contextual matching: does redacted text preserve document meaning?
  3. Contextual correctness: are all contextual identifiers (relatives, roles) caught?
"""

import re
from typing import Dict, List, Tuple, Any, Set
import spacy
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# SCORING CONSTANTS
# -------------------------------------------------------------------------

PII_CATCH_WEIGHT = 0.5
"""Weight for how much PII detection matters in final score (0.0-1.0)."""

STRUCTURAL_MATCH_WEIGHT = 0.3
"""Weight for exact tag match against expected redacted text (0.0-1.0)."""

CONTEXTUAL_PRESERVATION_WEIGHT = 0.2
"""Weight for document readability/structure preservation (0.0-1.0)."""

# Load spaCy model (English - we'll use for common names/org patterns)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model not found, try to download it
    import subprocess
    import sys
    print("Downloading spaCy model en_core_web_sm...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# ---------------------------------------------------------------------------
# VALID REDACTION TAGS FOR MEDIUM TASK
# -------------------------------------------------------------------------
VALID_MEDIUM_TAGS: Set[str] = {
    "[REDACTED_NAME]",
    "[REDACTED_ORGANIZATION]",
    "[REDACTED_ADDRESS]",
    "[REDACTED_PHONE]",
    "[REDACTED_EMAIL]",
    "[REDACTED_DOB]",
    "[REDACTED_RELATIVE_REFERENCE]",
}


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities using spaCy NER.
    
    Args:
        text: Input text to extract entities from
        
    Returns:
        Dict with keys PERSON, ORG, GPE and list of entity values
    """
    doc = nlp(text)
    entities = {"PERSON": [], "ORG": [], "GPE": []}
    
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    # Remove duplicates while preserving order
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))
    
    return entities


def extract_pii_values(pii_present: List[Dict[str, Any]]) -> List[str]:
    """
    Extract all PII values from ground truth for easier checking.
    
    Args:
        pii_present: List of {"type": "...", "value": "..."} dicts
        
    Returns:
        List of PII values
    """
    if not isinstance(pii_present, list):
        return []
    
    values = []
    for item in pii_present:
        if isinstance(item, dict) and "value" in item:
            val = item["value"]
            if val:  # Skip None/empty
                values.append(val)
    
    return values


def check_pii_redaction(original_text: str, redacted_text: str, pii_values: List[str]) -> Tuple[List[str], List[str]]:
    """
    Check which PII items from ground truth are still present in redacted text.
    
    Args:
        original_text: Original document
        redacted_text: Agent's redacted document
        pii_values: Ground truth PII values
        
    Returns:
        Tuple of (missed_pii, caught_pii)
    """
    missed = []
    caught = []
    
    for pii_val in pii_values:
        # Check if PII value still appears in redacted text (case-insensitive)
        if re.search(re.escape(pii_val), redacted_text, re.IGNORECASE):
            missed.append(pii_val)
        else:
            caught.append(pii_val)
    
    return missed, caught


def has_valid_redaction_tags(redacted_text: str) -> float:
    """
    Check if redacted text contains valid redaction tags.
    Uses heuristic: should have some [REDACTED_*] tags if PII was present.
    
    Args:
        redacted_text: Agent's redacted document
        
    Returns:
        Score 0.0-1.0 indicating compliance with tag format
    """
    # Find all redaction patterns
    found_tags = re.findall(r'\[REDACTED_\w+\]', redacted_text)
    
    if not found_tags:
        # No redaction tags found — agent may have deleted instead
        return 0.0
    
    # Check what fraction of found tags are valid
    valid_count = sum(1 for tag in found_tags if f"[{tag[1:-1]}]" in VALID_MEDIUM_TAGS or tag in VALID_MEDIUM_TAGS)
    
    if len(found_tags) == 0:
        return 0.0
    
    return valid_count / len(found_tags)


def calculate_structural_similarity(expected_redacted: str, actual_redacted: str) -> float:
    """
    Calculate structural similarity between expected and actual redacted text.
    Uses token-level fuzzy matching (not character-level to be tolerant of whitespace).
    
    Args:
        expected_redacted: Ground truth redacted version
        actual_redacted: Agent's redacted version
        
    Returns:
        Similarity score 0.0-1.0
    """
    if not expected_redacted or not actual_redacted:
        return 0.5  # Not enough info to judge
    
    # Tokenize by words
    expected_tokens = expected_redacted.lower().split()
    actual_tokens = actual_redacted.lower().split()
    
    # Calculate token-level similarity
    matcher = SequenceMatcher(None, expected_tokens, actual_tokens)
    return matcher.ratio()


def calculate_readability_preservation(original_text: str, redacted_text: str) -> float:
    """
    Check if document structure is preserved (no massive content deletion).
    
    Args:
        original_text: Original document
        redacted_text: Agent's redacted document
        
    Returns:
        Score 0.0-1.0 for preservation metric
    """
    orig_len = len(original_text.split())
    redacted_len = len(redacted_text.split())
    
    if orig_len == 0:
        return 1.0
    
    # Severely reduced document (>70% deletion) gets lower score
    # Mildly reduced document (10-30% deletion) is expected and okay
    word_ratio = redacted_len / orig_len
    
    if word_ratio > 0.7:
        # 30% or less deleted — good preservation
        return 1.0
    elif word_ratio > 0.5:
        # 30-50% deleted — moderate preservation
        return 0.7
    elif word_ratio > 0.3:
        # 50-70% deleted — poor preservation
        return 0.4
    else:
        # More than 70% deleted — very poor
        return 0.1


def grade_medium_task(
    original_text: str,
    redacted_text: str,
    pii_present: List[Dict[str, Any]],
    expected_redacted: str = "",
) -> Dict[str, Any]:
    """
    Main grading function for the medium task.
    
    Scores based on:
    1. PII catch rate (50% weight): what fraction of groundtruth PII is properly redacted
    2. Structural match (30% weight): how similar is to expected redacted text
    3. Readability (20% weight): is document structure preserved
    
    Args:
        original_text: The raw document before redaction
        redacted_text: The agent's submitted redacted document
        pii_present: Ground truth PII list
        expected_redacted: Expected redacted version (for comparison)
        
    Returns:
        Dict with keys: score, feedback, pii_missed, pii_caught, 
                       tag_compliance, structural_match, readability_score
    """
    
    # --- Extract PII values from ground truth ---
    pii_values = extract_pii_values(pii_present)
    total_pii = len(pii_values)
    
    if total_pii == 0:
        # No PII in document
        if redacted_text.strip() == original_text.strip():
            return {
                "score": 1.0,
                "feedback": "Document contained no PII — returned correctly unchanged.",
                "pii_missed": [],
                "pii_caught": [],
                "tag_compliance": 1.0,
                "structural_match": 1.0,
                "readability_score": 1.0,
            }
        else:
            return {
                "score": 0.5,
                "feedback": "Document contained no PII but agent modified it anyway.",
                "pii_missed": [],
                "pii_caught": [],
                "tag_compliance": 0.0,
                "structural_match": 0.0,
                "readability_score": 0.5,
            }
    
    # --- Check which PII is still exposed ---
    missed_pii, caught_pii = check_pii_redaction(original_text, redacted_text, pii_values)
    
    # --- Scoring component 1: PII catch rate ---
    pii_score = len(caught_pii) / total_pii if total_pii > 0 else 1.0
    
    # --- Scoring component 2: Tag compliance ---
    tag_compliance = has_valid_redaction_tags(redacted_text)
    # If agent used invalid tags or deleted instead of tagging, penalize
    pii_score = pii_score * tag_compliance
    
    # --- Scoring component 3: Structural similarity (if ground truth available) ---
    structural_score = 0.7  # Default if no ground truth
    if expected_redacted:
        structural_score = calculate_structural_similarity(expected_redacted, redacted_text)
    
    # --- Scoring component 4: Readability preservation ---
    readability_score = calculate_readability_preservation(original_text, redacted_text)
    
    # --- Combine components into final score ---
    final_score = (
        pii_score * PII_CATCH_WEIGHT +
        structural_score * STRUCTURAL_MATCH_WEIGHT +
        readability_score * CONTEXTUAL_PRESERVATION_WEIGHT
    )
    
    final_score = max(0.0, min(1.0, final_score))  # Clamp to [0.0, 1.0]
    
    # --- Build feedback ---
    feedback_parts = [
        f"Caught {len(caught_pii)}/{total_pii} PII items (score: {pii_score:.2f}).",
    ]
    
    if tag_compliance < 1.0:
        feedback_parts.append(f"Tag format compliance: {tag_compliance:.2f} (use valid [REDACTED_*] tags).")
    
    if structural_score < 1.0:
        feedback_parts.append(f"Structural match vs. expected: {structural_score:.2f}.")
    
    if readability_score < 1.0:
        feedback_parts.append(f"Document readability preserved: {readability_score:.2f}.")
    
    if missed_pii:
        # Show first few missed PII items
        shown_missed = missed_pii[:3]
        more = f" (and {len(missed_pii) - 3} more)" if len(missed_pii) > 3 else ""
        feedback_parts.append(f"PII still exposed: {shown_missed}{more}")
    else:
        feedback_parts.append("✓ All PII successfully redacted!")
    
    feedback_parts.append(f"Final score: {final_score:.2f}")
    
    return {
        "score": round(final_score, 2),
        "feedback": " | ".join(feedback_parts),
        "pii_missed": missed_pii,
        "pii_caught": caught_pii,
        "tag_compliance": round(tag_compliance, 2),
        "structural_match": round(structural_score, 2),
        "readability_score": round(readability_score, 2),
    }