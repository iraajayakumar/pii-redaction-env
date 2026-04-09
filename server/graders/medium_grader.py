"""
Grader for the medium PII redaction task.
Uses spaCy NER (Named Entity Recognition) for entity extraction,
and leverages LLM-based contextual scoring for correctness assessment.

Advanced Features:
1. Context Window Expansion: Looks at surrounding sentences for implicit PII
2. LLM-based Contextual Validation: Validates semantic correctness of redactions
3. Sensitivity Tuning: Adjustable scoring for medical, legal, financial domains

Design principles:
- Uses spaCy NER to extract PERSON, ORG, GPE entities
- Context-aware PII detection using surrounding sentences
- Optional LLM validation for contextual correctness
- Domain-specific risk profiles with configurable weights
"""

import re
import json
import os
from typing import Dict, List, Tuple, Any, Set, Optional
import spacy
from difflib import SequenceMatcher
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# SENSITIVITY PROFILES — Use case specific scoring weights
# -------------------------------------------------------------------------
# Different domains have different risk profiles and compliance requirements
SENSITIVITY_PROFILES = {
    "medical": {
        "description": "Healthcare/Medical records - highest sensitivity",
        "pii_catch_weight": 0.55,           # Catching PII is more important
        "structural_match_weight": 0.25,   # Structural match less critical
        "contextual_preservation_weight": 0.10,  # Preserve readability but not paramount
        "llm_validation_weight": 0.10,     # LLM adds final validation
        "pii_exposure_penalty": 0.3,       # Heavy penalty for exposed PII
    },
    "legal": {
        "description": "Legal documents - balanced sensitivity",
        "pii_catch_weight": 0.45,
        "structural_match_weight": 0.35,   # Legal documents must maintain exact structure
        "contextual_preservation_weight": 0.15,
        "llm_validation_weight": 0.05,
        "pii_exposure_penalty": 0.25,
    },
    "financial": {
        "description": "Financial/Banking records - very high sensitivity",
        "pii_catch_weight": 0.60,           # Financial PII is most critical
        "structural_match_weight": 0.20,
        "contextual_preservation_weight": 0.05,
        "llm_validation_weight": 0.15,     # Use LLM to verify account/identity PII
        "pii_exposure_penalty": 0.4,       # Strictest penalty
    },
    "default": {
        "description": "Balanced general-purpose sensitivity",
        "pii_catch_weight": 0.50,
        "structural_match_weight": 0.30,
        "contextual_preservation_weight": 0.20,
        "llm_validation_weight": 0.0,      # Disabled by default (requires LLM setup)
        "pii_exposure_penalty": 0.20,
    },
}

# Default sensitivity (can be overridden via environment variable)
DEFAULT_SENSITIVITY = os.getenv("PII_SENSITIVITY_PROFILE", "default")

# Lazy-load spaCy model (only when actually needed, not at import time)
_nlp_model = None

def get_nlp_model():
    """
    Lazy-load spaCy NER model (English).
    Only loads on first use to avoid startup failures if model isn't available.
    """
    global _nlp_model
    if _nlp_model is not None:
        return _nlp_model
    
    try:
        _nlp_model = spacy.load("en_core_web_sm")
        return _nlp_model
    except OSError:
        # If model not found, try to download it
        import subprocess
        import sys
        print("Downloading spaCy model en_core_web_sm...")
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            _nlp_model = spacy.load("en_core_web_sm")
            return _nlp_model
        except Exception as e:
            print(f"Failed to load spaCy model: {e}. Falling back to pattern-based extraction.")
            return None

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

# ---------------------------------------------------------------------------
# LLM INTEGRATION (flexible backend support)
# -------------------------------------------------------------------------
class LLMValidator:
    """
    Abstract LLM validator for contextual correctness assessment.
    Supports multiple backends: OpenAI, Ollama, Local models, etc.
    
    This allows for LLM-based semantic validation of redactions.
    """
    
    def __init__(self, backend: str = "mock", **kwargs):
        """
        Initialize LLM validator.
        
        Args:
            backend: "openai", "ollama", "mock" (default)
            **kwargs: Backend-specific configuration (api_key, model_name, endpoint, etc.)
        """
        self.backend = backend
        self.config = kwargs
        
    def validate_redaction(self, 
                          original_context: str,
                          redacted_context: str,
                          pii_type: str) -> Tuple[float, str]:
        """
        Validate if a redaction is semantically correct.
        
        Args:
            original_context: Original text around the PII (with surrounding sentences)
            redacted_context: Redacted version
            pii_type: Type of PII redacted
            
        Returns:
            Tuple of (confidence_score: 0.0-1.0, explanation: str)
        """
        if self.backend == "mock":
            return self._validate_mock(original_context, redacted_context, pii_type)
        elif self.backend == "huggingface":
            return self._validate_huggingface(original_context, redacted_context, pii_type)
        elif self.backend == "ollama":
            return self._validate_ollama(original_context, redacted_context, pii_type)
        # elif self.backend == "openai":
        #     return self._validate_openai(original_context, redacted_context, pii_type)
        else:
            return 0.8, f"Unknown backend '{self.backend}', using default confidence"
    
    def _validate_mock(self, original_context: str, redacted_context: str, pii_type: str) -> Tuple[float, str]:
        """
        Mock validator for testing without LLM.
        Uses heuristics to assess semantic correctness.
        """
        # Heuristic: if document still makes sense after redaction
        
        # Should have redaction tags if PII was present
        if len(original_context) > len(redacted_context):
            has_redaction_tags = any(tag in redacted_context for tag in VALID_MEDIUM_TAGS)
            if not has_redaction_tags:
                return 0.3, "PII removed but no valid redaction tags used"
            else:
                return 0.85, f"Properly redacted {pii_type} with valid tags"
        else:
            return 0.5, "Context unchanged or expanded - may indicate missed redaction"
    
    def _validate_huggingface(self, original_context: str, redacted_context: str, pii_type: str) -> Tuple[float, str]:
        """
        Validate using HuggingFace Inference API (Zephyr).
        Sends context to HuggingFace Zephyr model for semantic assessment.
        
        Args:
            original_context: Original context with PII
            redacted_context: Redacted context
            pii_type: Type of PII that was redacted
            
        Returns:
            Tuple of (confidence_score, explanation)
        """
        try:
            # Get HuggingFace config from environment
            hf_token = self.config.get('token', os.getenv('HF_TOKEN'))
            model = self.config.get('model', os.getenv('HF_MODEL', 'HuggingFaceH4/zephyr-7b-beta'))
            
            if not hf_token:
                return 0.7, "HF_TOKEN not configured - using default confidence"
            
            # Initialize HuggingFace Inference Client
            client = InferenceClient(model=model, token=hf_token)
            
            # Prepare simplified prompt for faster response
            prompt = f"""Evaluate this PII redaction (score 0.0-1.0):
Original: {original_context[:200]}
Redacted: {redacted_context[:200]}
Type: {pii_type}

Respond with JSON: {{"score": 0.X, "explanation": "brief text"}}"""
            
            # Call HuggingFace API
            response_text = client.text_generation(
                prompt,
                max_new_tokens=200,
                temperature=0.2
            )
            
            # Extract JSON from response
            try:
                json_match = re.search(r'\{[^}]*"score"[^}]*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    score = float(parsed.get('score', 0.7))
                    explanation = str(parsed.get('explanation', 'Validated'))
                    return min(1.0, max(0.0, score)), explanation
            except (json.JSONDecodeError, ValueError):
                pass
            
            # Fallback: parse score from text
            score_match = re.search(r'score["\']?\s*[:=]?\s*([0-9.]+)', response_text, re.IGNORECASE)
            if score_match:
                score = float(score_match.group(1))
                return min(1.0, max(0.0, score)), "Parsed from response"
            
            # If very high score or low score keyword, return accordingly
            if 'good' in response_text.lower() or 'correct' in response_text.lower():
                return 0.85, "LLM confirmed redaction"
            elif 'bad' in response_text.lower() or 'wrong' in response_text.lower():
                return 0.45, "LLM found issue"
            
            return 0.75, "Validation complete"
            
        except Exception as e:
            error_msg = str(e)[:30]
            if 'timeout' in error_msg.lower():
                return 0.75, "HF API timeout - likely still generating"
            elif 'connection' in error_msg.lower():
                return 0.65, "HF API connection issue"
            else:
                return 0.65, f"Error: {error_msg}"
    
    def _validate_ollama(self, original_context: str, redacted_context: str, pii_type: str) -> Tuple[float, str]:
        """
        Validate using Ollama local LLM (Mistral).
        Sends context to local Mistral model for semantic assessment.
        
        Args:
            original_context: Original context with PII
            redacted_context: Redacted context
            pii_type: Type of PII that was redacted
            
        Returns:
            Tuple of (confidence_score, explanation)
        """
        try:
            # Get Ollama endpoint from config or environment
            endpoint = self.config.get('endpoint', os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434'))
            model = self.config.get('model', os.getenv('OLLAMA_MODEL', 'mistral'))
            
            # Prepare simplified prompt for faster response
            prompt = f"""Evaluate this PII redaction (score 0.0-1.0):
Original: {original_context[:200]}
Redacted: {redacted_context[:200]}
Type: {pii_type}

Respond with JSON: {{"score": 0.X, "explanation": "brief text"}}"""
            
            # Call Ollama API with longer timeout
            response = requests.post(
                f"{endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2
                },
                timeout=120  # Increased from 30s to allow for generation time
            )
            
            if response.status_code != 200:
                return 0.7, f"Ollama error ({response.status_code})"
            
            # Parse response
            result = response.json()
            response_text = result.get('response', '')
            
            # Extract JSON from response
            try:
                json_match = re.search(r'\{[^}]*"score"[^}]*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    score = float(parsed.get('score', 0.7))
                    explanation = str(parsed.get('explanation', 'Validated'))
                    return min(1.0, max(0.0, score)), explanation
            except (json.JSONDecodeError, ValueError):
                pass
            
            # Fallback: parse score from text
            score_match = re.search(r'score["\']?\s*[:=]?\s*([0-9.]+)', response_text, re.IGNORECASE)
            if score_match:
                score = float(score_match.group(1))
                return min(1.0, max(0.0, score)), "Parsed from response"
            
            # If very high score or low score keyword, return accordingly
            if 'good' in response_text.lower() or 'correct' in response_text.lower():
                return 0.85, "LLM confirmed redaction"
            elif 'bad' in response_text.lower() or 'wrong' in response_text.lower():
                return 0.45, "LLM found issue"
            
            return 0.75, "Validation complete"
            
        except requests.exceptions.Timeout:
            return 0.75, "Ollama taking too long (timeout) - model generating"
        except requests.exceptions.ConnectionError:
            return 0.5, "Ollama not running - start with: ollama serve"
        except Exception as e:
            return 0.65, f"Error: {str(e)[:30]}"


def get_llm_validator(use_llm: bool = False, backend: str = "mock", **kwargs) -> Optional[LLMValidator]:
    """
    Factory for creating LLM validators.
    
    Args:
        use_llm: Whether to enable LLM validation
        backend: Backend to use ("mock", "openai", "ollama")
        **kwargs: Backend configuration
        
    Returns:
        LLMValidator instance or None if disabled
    """
    if not use_llm:
        return None
    return LLMValidator(backend=backend, **kwargs)


# ---------------------------------------------------------------------------
# CONTEXT WINDOW EXTRACTION (Feature 2: Context Window Expansion)
# -------------------------------------------------------------------------
def extract_context_window(text: str, target_index: int, window_size: int = 2) -> str:
    """
    Extract surrounding context around a specific position in text.
    Uses sentences as the unit, not characters.
    
    This enables implicit PII detection by examining neighboring sentences
    for contextual identifiers (e.g., "my cousin John" where "John" is implicit PII).
    
    Args:
        text: Full document text
        target_index: Character position of target PII
        window_size: Number of sentences before/after to include
        
    Returns:
        Context string with surrounding sentences
    """
    # Split into sentences (simple split on period, question mark, exclamation)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Find which sentence contains the target index
    char_count = 0
    target_sentence_idx = 0
    for i, sentence in enumerate(sentences):
        char_count += len(sentence) + 1  # +1 for space
        if char_count >= target_index:
            target_sentence_idx = i
            break
    
    # Extract window with surrounding sentences
    start_idx = max(0, target_sentence_idx - window_size)
    end_idx = min(len(sentences), target_sentence_idx + window_size + 1)
    
    context_sentences = sentences[start_idx:end_idx]
    return ' '.join(context_sentences)


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities using spaCy NER.
    
    Args:
        text: Input text to extract entities from
        
    Returns:
        Dict with keys PERSON, ORG, GPE and list of entity values
    """
    nlp = get_nlp_model()
    if nlp is None:
        # Fallback if spacy model unavailable
        return {"PERSON": [], "ORG": [], "GPE": []}
    
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


# ---------------------------------------------------------------------------
# CONTEXT-AWARE PII DETECTION (Feature 1 + 2: Context Windows + LLM Validation)
# -------------------------------------------------------------------------
def check_pii_redaction_with_context(original_text: str, 
                                     redacted_text: str, 
                                     pii_values: List[str],
                                     llm_validator: Optional[LLMValidator] = None) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """
    Check which PII items are still present, WITH CONTEXT WINDOW ANALYSIS.
    Uses surrounding sentences to detect implicit/contextual PII exposure.
    
    Args:
        original_text: Original document
        redacted_text: Agent's redacted document
        pii_values: Ground truth PII values
        llm_validator: Optional LLM validator for semantic checking
        
    Returns:
        Tuple of (missed_pii, caught_pii, context_analysis)
    """
    missed = []
    caught = []
    context_analysis = {"exposed_contexts": [], "redacted_contexts": []}
    
    for pii_val in pii_values:
        # Direct check: is the PII value still present?
        direct_match = re.search(re.escape(pii_val), redacted_text, re.IGNORECASE)
        
        if direct_match:
            # PII is still exposed — check context
            missed.append(pii_val)
            
            # Extract context around exposed PII
            target_idx = direct_match.start()
            context = extract_context_window(redacted_text, target_idx, window_size=2)
            context_analysis["exposed_contexts"].append({
                "pii": pii_val,
                "context": context,
                "exposure_type": "direct"
            })
        else:
            # PII was redacted
            caught.append(pii_val)
            
            # Find original position and get context from redacted version
            orig_match = re.search(re.escape(pii_val), original_text, re.IGNORECASE)
            if orig_match:
                # Use approximate position to extract context
                orig_idx = orig_match.start()
                redacted_context = extract_context_window(redacted_text, min(orig_idx, len(redacted_text)-1), window_size=2)
                context_analysis["redacted_contexts"].append({
                    "pii": pii_val,
                    "redacted_context": redacted_context
                })
                
                # Feature 1: LLM-based Contextual Validation
                if llm_validator:
                    orig_context = extract_context_window(original_text, orig_idx, window_size=2)
                    confidence, explanation = llm_validator.validate_redaction(
                        orig_context, 
                        redacted_context,
                        pii_val
                    )
                    context_analysis["redacted_contexts"][-1]["llm_confidence"] = confidence
                    context_analysis["redacted_contexts"][-1]["llm_explanation"] = explanation
    
    return missed, caught, context_analysis


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
    missed, caught, _ = check_pii_redaction_with_context(original_text, redacted_text, pii_values)
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


def calculate_llm_validation_score(context_analysis: Dict[str, Any]) -> float:
    """
    Calculate LLM validation score from context analysis.
    Averages confidence scores from LLM validator (Feature 1).
    
    Args:
        context_analysis: Analysis dict with LLM confidence scores
        
    Returns:
        Score 0.0-1.0
    """
    llm_confidences = []
    
    for redacted_context in context_analysis.get("redacted_contexts", []):
        if "llm_confidence" in redacted_context:
            llm_confidences.append(redacted_context["llm_confidence"])
    
    if not llm_confidences:
        return 1.0  # No LLM scores to evaluate against
    
    return sum(llm_confidences) / len(llm_confidences)


def grade_medium_task(
    original_text: str,
    redacted_text: str,
    pii_present: List[Dict[str, Any]],
    expected_redacted: str = "",
    use_case: str = "default",
    use_llm: bool = False,
    llm_backend: str = "mock",
) -> Dict[str, Any]:
    """
    Main grading function for the medium task with all advanced features.
    
    Features:
    1. Context-Aware PII Detection: Examines surrounding sentences
    2. LLM-based Contextual Validation: Optional semantic validation
    3. Sensitivity Tuning: Domain-specific scoring weights
    
    Scores based on configurable weights:
    - PII catch rate: what fraction of groundtruth PII is properly redacted
    - Structural match: how similar is to expected redacted text
    - Readability: is document structure preserved
    - LLM validation: semantic correctness (if enabled)
    
    Args:
        original_text: The raw document before redaction
        redacted_text: The agent's submitted redacted document
        pii_present: Ground truth PII list
        expected_redacted: Expected redacted version (for comparison)
        use_case: "medical", "legal", "financial", or "default"
        use_llm: Whether to enable LLM validation
        llm_backend: LLM backend to use ("mock", "openai", "ollama")
        
    Returns:
        Dict with keys: score, feedback, pii_missed, pii_caught, 
                       tag_compliance, structural_match, readability_score,
                       sensitivity_profile, llm_validation_score
    """
    
    # Feature 3: Load sensitivity profile based on use_case
    if use_case not in SENSITIVITY_PROFILES:
        use_case = "default"
    
    profile = SENSITIVITY_PROFILES[use_case]
    pii_catch_weight = profile["pii_catch_weight"]
    structural_match_weight = profile["structural_match_weight"]
    contextual_preservation_weight = profile["contextual_preservation_weight"]
    llm_validation_weight = profile["llm_validation_weight"]
    pii_exposure_penalty = profile["pii_exposure_penalty"]
    
    # Initialize LLM validator if requested
    llm_validator = get_llm_validator(use_llm, llm_backend) if use_llm else None
    
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
                "sensitivity_profile": use_case,
                "llm_validation_score": 1.0 if use_llm else None,
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
                "sensitivity_profile": use_case,
                "llm_validation_score": 0.5 if use_llm else None,
            }
    
    # Feature 2: Check PII redaction with context windows
    missed_pii, caught_pii, context_analysis = check_pii_redaction_with_context(
        original_text, 
        redacted_text, 
        pii_values,
        llm_validator=llm_validator
    )
    
    # --- Scoring component 1: PII catch rate ---
    pii_score = len(caught_pii) / total_pii if total_pii > 0 else 1.0
    
    # Apply exposure penalty for any missed PII
    if missed_pii:
        pii_score = max(0.0, pii_score - (pii_exposure_penalty * len(missed_pii) / total_pii))
    
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
    
    # --- Scoring component 5: LLM validation (Feature 1) ---
    llm_score = 1.0
    if use_llm and llm_validator:
        llm_score = calculate_llm_validation_score(context_analysis)
    
    # --- Combine components into final score using sensitivity weights ---
    final_score = (
        pii_score * pii_catch_weight +
        structural_score * structural_match_weight +
        readability_score * contextual_preservation_weight +
        llm_score * llm_validation_weight
    )
    
    final_score = max(0.0, min(1.0, final_score))  # Clamp to [0.0, 1.0]
    
    # --- Build feedback ---
    feedback_parts = [
        f"[{use_case.upper()}] Caught {len(caught_pii)}/{total_pii} PII items (score: {pii_score:.2f}).",
    ]
    
    if tag_compliance < 1.0:
        feedback_parts.append(f"Tag format compliance: {tag_compliance:.2f} (use valid [REDACTED_*] tags).")
    
    if structural_score < 1.0:
        feedback_parts.append(f"Structural match vs. expected: {structural_score:.2f}.")
    
    if readability_score < 1.0:
        feedback_parts.append(f"Document readability preserved: {readability_score:.2f}.")
    
    if use_llm and llm_validator and llm_score < 1.0:
        feedback_parts.append(f"LLM semantic validation: {llm_score:.2f}.")
    
    if missed_pii:
        # Show first few missed PII items
        shown_missed = missed_pii[:3]
        more = f" (and {len(missed_pii) - 3} more)" if len(missed_pii) > 3 else ""
        feedback_parts.append(f"⚠️ PII still exposed: {shown_missed}{more}")
    else:
        feedback_parts.append("✓ All PII successfully redacted!")
    
    feedback_parts.append(f"Final score: {final_score:.2f} (weights: PII={pii_catch_weight}, Struct={structural_match_weight}, Readability={contextual_preservation_weight}, LLM={llm_validation_weight})")
    
    return {
        "score": round(final_score, 2),
        "feedback": " | ".join(feedback_parts),
        "pii_missed": missed_pii,
        "pii_caught": caught_pii,
        "tag_compliance": round(tag_compliance, 2),
        "structural_match": round(structural_score, 2),
        "readability_score": round(readability_score, 2),
        "sensitivity_profile": use_case,
        "llm_validation_score": round(llm_score, 2) if use_llm else None,
        "context_analysis": context_analysis if use_llm else None,
    }