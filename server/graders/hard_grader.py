"""
Grader for the hard PII redaction task.

Hard Task: De-anonymisation Defense
===================================

Objective: Agent must redact a document so thoroughly that even with quasi-identifier attacks,
the person cannot be re-identified.

Design:
-------
1. Agent submits redacted document
2. Judge evaluates: "Can someone still identify this person?"
   - Uses quasi-identifier combinations (age + rare_disease + workplace, etc.)
3. If YES (re-identifiable):
   - Score decreases
   - Agent gets another attempt (max 3 total)
4. If NO (not re-identifiable):
   - Episode ends successfully
   - Score based on: baseline + how quickly defended

Scoring Formula:
----------------
final_score = 0.5 * medium_baseline + 0.5 * adversarial_defense

where:
  medium_baseline = grade_medium_task(original, redacted, pii)
  adversarial_defense = (MAX_ATTEMPTS - actual_attempts) / MAX_ATTEMPTS

Example:
  - Baseline redaction good (medium score 0.85)
  - Defended successfully in 1 attempt out of 3
  - Score = 0.5 * 0.85 + 0.5 * (3-1)/3 = 0.425 + 0.333 = 0.758
"""

import re
import os
import json
import requests
from typing import Dict, List, Tuple, Any, Optional
from dotenv import load_dotenv
from .medium_grader import grade_medium_task

# Load environment variables
load_dotenv()

# Maximum attempts to defend against re-identification
MAX_HARD_ATTEMPTS = 3

# Known quasi-identifier patterns that can identify someone
QUASI_IDENTIFIER_PATTERNS = {
    "rare_condition_combinations": [
        {
            "pattern": r"(age|years old|aged).*?(cardiologist|nephrologist|infectious disease).*?(Takayasu|ARDS|Wegener)",
            "risk": "high",
            "description": "Rare condition + specialty + age = highly identifying"
        },
        {
            "pattern": r"(leukemia|lymphoma|cancer).*?(pediatric|childhood).*?(\d{1,2}\s+years?).*?(published|authored)",
            "risk": "high",
            "description": "Pediatric cancer specialist with publications = identifying"
        },
        {
            "pattern": r"(trained at|fellowship|completed|degree from).*(AIIMS|CMC|Apollo|Johns Hopkins|NIH).*?(age|years old).*?(rare)",
            "risk": "medium",
            "description": "Specific training + rare expertise + location = identifying"
        }
    ],
    "location_specialty_age": [
        {
            "pattern": r"(age|years old).*?(doctor|specialist|professor).*?(Delhi|Mumbai|Chennai|Bangalore).*?(department|specialty)",
            "risk": "medium",
            "description": "Age + specialty + location combination"
        }
    ],
    "rare_publication_combination": [
        {
            "pattern": r"(published|authored).*?(papers?|articles?).*?(rare|uncommon|unique).*?(condition|disease|syndrome)",
            "risk": "high",
            "description": "Published on rare topic = potentially identifying"
        }
    ],
    "achievement_combination": [
        {
            "pattern": r"(fellowship|award|prize).*?(Microsoft|Google|Facebook|MIT|Stanford).*?(age|year).*?(first author)",
            "risk": "high",
            "description": "Prestigious award + young age + first author = identifying"
        }
    ]
}


def ollama_quasi_identifier_judge(redacted_text: str, endpoint: str = None, model: str = None) -> Tuple[bool, str, float]:
    """
    Real LLM-based judge using Ollama/Mistral for re-identification assessment.
    
    Uses Mistral-7B to evaluate if quasi-identifiers still allow re-identification.
    Asks: "Can you identify who this person is from this redacted document?"
    
    Args:
        redacted_text: The redacted document
        endpoint: Ollama endpoint (default: localhost:11434)
        model: Model name (default: mistral)
        
    Returns:
        Tuple of (is_reidentifiable, reasoning, confidence)
    """
    try:
        # Get Ollama config
        endpoint = endpoint or os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')
        model = model or os.getenv('OLLAMA_MODEL', 'mistral')
        
        # Prepare prompt for re-identification assessment
        prompt = f"""You are a privacy expert assessing PII redaction quality.

Task: Determine if this redacted document still allows re-identification through quasi-identifiers.

Redacted Document:
{redacted_text[:1000]}

Analyze: Can someone identify who this person is from remaining quasi-identifiers (age + rare condition + location + specialty, etc.)?

Respond with JSON:
{{
  "can_reidentify": true/false,
  "reasoning": "brief explanation",
  "confidence": 0.0-1.0
}}

Be strict - any combination of rare attributes that could narrow down identity counts as reidentifiable."""
        
        # Call Ollama API
        response = requests.post(
            f"{endpoint}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1  # Low temperature for consistent assessment
            },
            timeout=120
        )
        
        if response.status_code != 200:
            return True, f"Ollama error ({response.status_code}) - defaulting to conservative assessment", 0.5
        
        # Parse response
        result = response.json()
        response_text = result.get('response', '')
        
        # Extract JSON from response
        try:
            json_match = re.search(r'\{[^}]*"can_reidentify"[^}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                is_reid = parsed.get('can_reidentify', True)  # Default to yes if unclear
                reasoning = parsed.get('reasoning', 'LLM assessment')
                confidence = float(parsed.get('confidence', 0.7))
                return bool(is_reid), reasoning, float(confidence)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback: parse keywords from response
        if 'cannot' in response_text.lower() or 'not reidentifiable' in response_text.lower():
            return False, "LLM: Cannot re-identify from quasi-identifiers", 0.75
        elif 'can' in response_text.lower() or 'reidentifiable' in response_text.lower():
            return True, "LLM: Can re-identify from quasi-identifiers", 0.75
        
        # Default conservative assessment
        return True, "LLM assessment inconclusive - conservative assessment", 0.6
        
    except requests.exceptions.Timeout:
        return True, "Ollama timeout - defaulting to conservative (reidentifiable) assessment", 0.5
    except requests.exceptions.ConnectionError:
        return True, "Ollama not running - defaulting to conservative assessment", 0.4
    except Exception as e:
        return True, f"LLM judge error: {str(e)[:50]}", 0.3


def mock_quasi_identifier_judge(redacted_text: str) -> Tuple[bool, str, float]:
    """
    Mock judge that checks for quasi-identifier vulnerabilities (fast, deterministic).
    
    This is used for testing. For production, use ollama_quasi_identifier_judge().
    
    Args:
        redacted_text: The redacted document
        
    Returns:
        Tuple of (is_reidentifiable, reasoning, confidence)
        - is_reidentifiable: True if someone can re-identify
        - reasoning: Explanation of what makes it identifiable
        - confidence: How certain the judge is (0.0-1.0)
    """
    
    # Check for dangerous quasi-identifier patterns
    found_patterns = []
    highest_risk = "none"
    
    for pattern_category, patterns in QUASI_IDENTIFIER_PATTERNS.items():
        for pattern_obj in patterns:
            if re.search(pattern_obj["pattern"], redacted_text, re.IGNORECASE):
                found_patterns.append(pattern_obj["description"])
                if pattern_obj["risk"] == "high":
                    highest_risk = "high"
                elif pattern_obj["risk"] == "medium" and highest_risk != "high":
                    highest_risk = "medium"
    
    # Decision logic
    if highest_risk == "high" and len(found_patterns) >= 2:
        # Multiple high-risk patterns found
        reasoning = f"Found {len(found_patterns)} quasi-identifier patterns that together enable re-identification: {', '.join(found_patterns[:2])}"
        return True, reasoning, 0.9
    
    elif highest_risk == "high" and len(found_patterns) >= 1:
        # Single high-risk pattern
        reasoning = f"Found high-risk quasi-identifier: {found_patterns[0]}"
        return True, reasoning, 0.85
    
    elif highest_risk == "medium" and len(found_patterns) >= 3:
        # Multiple medium-risk patterns
        reasoning = f"Found {len(found_patterns)} medium-risk quasi-identifier combinations"
        return True, reasoning, 0.7
    
    elif len(found_patterns) == 0:
        # Check for exposed [REDACTED_*] patterns
        redaction_tags = re.findall(r'\[REDACTED_\w+\]', redacted_text)
        if len(redaction_tags) > 0:
            # Document has proper redactions, no obvious patterns
            reasoning = "Document appears to have proper redaction of identifiable information"
            return False, reasoning, 0.95
        else:
            # No redactions found at all
            reasoning = "Document has no redaction tags - appears unregulated"
            return True, "Unredacted document", 0.8
    
    else:
        # Some patterns found but not immediately identifying
        reasoning = f"Found {len(found_patterns)} low-risk quasi-identifier pattern(s) - marginal case"
        return True, reasoning, 0.6


def extract_quasi_identifiers(text: str) -> List[str]:
    """
    Extract potential quasi-identifiers from text.
    
    Args:
        text: Document text
        
    Returns:
        List of identified quasi-identifier elements
    """
    quasi_ids = []
    
    # Extract age/date mentions
    ages = re.findall(r'(\d{1,2}[-\s]?year old|aged\s+\d{1,2})', text, re.IGNORECASE)
    if ages:
        quasi_ids.append(f"Age indicators: {ages}")
    
    # Extract specialty/profession
    specialties = re.findall(r'(cardiologist|oncologist|surgeon|neurologist|psychiatrist|nephrologist|pediatrician)', text, re.IGNORECASE)
    if specialties:
        quasi_ids.append(f"Specialties: {list(set(specialties))}")
    
    # Extract location
    locations = re.findall(r'(Delhi|Mumbai|Chennai|Bangalore|Kolkata|Hyderabad|Pune|Jaipur)', text, re.IGNORECASE)
    if locations:
        quasi_ids.append(f"Locations: {list(set(locations))}")
    
    # Extract rare conditions
    conditions = re.findall(r'(Takayasu|arteritis|leukemia|lymphoma|Wegener|ARDS)', text, re.IGNORECASE)
    if conditions:
        quasi_ids.append(f"Rare conditions: {list(set(conditions))}")
    
    # Extract institutions
    institutions = re.findall(r'(AIIMS|CMC|Apollo|Johns Hopkins|MIT|Stanford|NIH)', text, re.IGNORECASE)
    if institutions:
        quasi_ids.append(f"Institutions: {list(set(institutions))}")
    
    return quasi_ids


def grade_hard_task(original_text: str,
                   redacted_text: str,
                   pii_present: List[Dict[str, Any]],
                   use_llm_judge: bool = True,
                   ollama_endpoint: str = None,
                   ollama_model: str = None) -> Dict[str, Any]:
    """
    Grade the hard task: De-anonymisation defense.
    
    Logic:
    1. Get baseline score from medium task
    2. Evaluate if re-identification is still possible (real LLM or mock judge)
    3. Score based on: baseline + how many attempts needed to fully defend
    
    Args:
        original_text: Original document
        redacted_text: Agent's redacted version
        pii_present: List of PII that should be redacted
        use_llm_judge: Use real Ollama judge (True) or mock judge (False)
        ollama_endpoint: Ollama endpoint URL (default: localhost:11434)
        ollama_model: Model name (default: mistral)
        
    Returns:
        Dictionary with scoring details
    """
    
    # Get baseline score from medium task (without LLM for speed)
    medium_result = grade_medium_task(
        original_text=original_text,
        redacted_text=redacted_text,
        pii_present=pii_present,
        use_case="default",
        use_llm=False
    )
    
    medium_baseline = medium_result['score']
    
    # Evaluate re-identification vulnerability
    if use_llm_judge:
        # Use real Ollama/Mistral LLM judge
        is_reidentifiable, reasoning, confidence = ollama_quasi_identifier_judge(
            redacted_text,
            endpoint=ollama_endpoint,
            model=ollama_model
        )
    else:
        # Use fast mock judge (for testing/offline)
        is_reidentifiable, reasoning, confidence = mock_quasi_identifier_judge(redacted_text)
    
    # For now, simulate a single evaluation
    # (In real scenario with agent loop, this would track attempts)
    actual_attempts = 1  # Assume agent succeeds on first try for baseline
    
    if is_reidentifiable:
        # Vulnerability found - agent would need more attempts
        # For single-shot grading, penalize
        actual_attempts = 3  # Worst case
    
    # Calculate adversarial defense score
    # (max_attempts - actual_attempts) / max_attempts
    # If succeeded on attempt 1: (3 - 1) / 3 = 0.667
    # If needed all 3 attempts: (3 - 3) / 3 = 0.0
    adversarial_defense = (MAX_HARD_ATTEMPTS - actual_attempts) / MAX_HARD_ATTEMPTS
    
    # Final score: 50% baseline + 50% adversarial defense
    final_score = 0.5 * medium_baseline + 0.5 * adversarial_defense
    
    # Extract quasi-identifiers for analysis
    found_quasi_ids = extract_quasi_identifiers(redacted_text)
    
    return {
        "score": round(final_score, 3),
        "medium_baseline": round(medium_baseline, 3),
        "adversarial_defense": round(adversarial_defense, 3),
        "is_reidentifiable": is_reidentifiable,
        "reidentification_reasoning": reasoning,
        "judge_confidence": round(confidence, 3),
        "quasi_identifiers_found": found_quasi_ids,
        "pii_caught": medium_result.get('pii_caught', []),
        "pii_missed": medium_result.get('pii_missed', []),
        "attempts_to_defend": actual_attempts,
        "max_attempts": MAX_HARD_ATTEMPTS,
        "feedback": f"Baseline redaction: {medium_baseline:.2f}. "
                   f"Re-identification possible: {is_reidentifiable}. "
                   f"Defense: {'Good' if actual_attempts <= 1 else 'Needed improvement'}. "
                   f"Final score: {final_score:.3f}"
    }


# For future integration with multi-attempt loop:
def evaluate_redaction_with_attempts(original_text: str,
                                    initial_redacted: str,
                                    pii_present: List[Dict[str, Any]],
                                    max_attempts: int = MAX_HARD_ATTEMPTS) -> Dict[str, Any]:
    """
    Simulate full hard task with multiple re-redaction attempts.
    
    In actual deployment with an agent, this would:
    1. Evaluate initial redaction
    2. If re-identifiable, agent re-redacts
    3. Repeat until not re-identifiable or max attempts reached
    
    Args:
        original_text: Original document
        initial_redacted: Agent's first redaction attempt
        pii_present: List of PII
        max_attempts: Maximum re-attempts allowed
        
    Returns:
        Final grading with attempt history
    """
    
    current_redacted = initial_redacted
    attempts = []
    
    for attempt_num in range(1, max_attempts + 1):
        is_reid, reasoning, confidence = mock_quasi_identifier_judge(current_redacted)
        
        attempts.append({
            "attempt": attempt_num,
            "is_reidentifiable": is_reid,
            "reasoning": reasoning,
            "confidence": confidence
        })
        
        if not is_reid:
            # Successfully defended
            break
        
        # Would continue loop with agent's next redaction
        # For now, we stop here
    
    # Calculate final score
    medium_result = grade_medium_task(original_text, current_redacted, pii_present, 
                                     use_case="default", use_llm=False)
    actual_attempts = len(attempts)
    
    adversarial_defense = (max_attempts - actual_attempts) / max_attempts
    final_score = 0.5 * medium_result['score'] + 0.5 * adversarial_defense
    
    return {
        "score": round(final_score, 3),
        "medium_baseline": round(medium_result['score'], 3),
        "attempts": attempts,
        "successful": not attempts[-1]['is_reidentifiable'],
        "attempts_needed": len(attempts)
    }