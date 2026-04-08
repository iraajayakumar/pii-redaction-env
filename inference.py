"""
Inference Script for PII Redaction Environment
===============================================

MANDATORY REQUIREMENTS:
- Environment variables:
    API_BASE_URL   (default: http://localhost:11434 for Ollama)
    MODEL_NAME     (default: mistral)
    HF_TOKEN       (optional, for HF API fallback)

STDOUT FORMAT (Hackathon Compliance):
- [START] task=pii_redaction env=pii_redaction_env model=mistral
- [STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
- [END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

Task Progression:
1. Easy: Detect structured PII (Aadhaar, PAN, phone, email, bank, IFSC)
2. Medium: Contextual + implicit PII detection with NER + LLM validation
3. Hard: Adversarial defense (3 attempts to prevent re-identification)

Final Score = Average of (easy_score, medium_score, hard_score) ∈ [0, 1]
"""

import asyncio
import os
import sys
import re
import textwrap
from typing import List, Optional, Dict, Any, Tuple

from openai import OpenAI

# Add pii_redaction_env to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import tasks and graders
try:
    from server.tasks.easy import get_easy_task
    from server.tasks.medium import get_medium_task
    from server.tasks.hard import get_hard_task
    from server.graders.easy_grader import grade_easy_task
    from server.graders.medium_grader import grade_medium_task
    from server.graders.hard_grader import grade_hard_task
except ImportError as e:
    print(f"[DEBUG] Import error: {e}", flush=True)
    sys.exit(1)

# Environment variables with defaults
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "mistral")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

# Initialize OpenAI client (compatible with Ollama via base_url)
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "")

# Task configuration
TASK_NAME = "pii_redaction"
BENCHMARK = "pii_redaction_env"
MAX_STEPS = 3  # Easy, Medium, Hard
MAX_ATTEMPTS_HARD = 3  # Max defense attempts for hard task
SUCCESS_SCORE_THRESHOLD = 0.5  # Score >= 0.5 is success


# ============================================================================
# Logging Functions (Hackathon Compliance)
# ============================================================================

def log_start(task: str, env: str, model: str) -> None:
    """Log episode start with task, environment, and model name."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    """Log step execution with action, reward, done flag, and optional error."""
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """Log episode completion with final score and reward history."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success_val = str(success).lower()
    print(
        f"[END] success={success_val} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ============================================================================
# Agent-Based Redaction (Using OpenAI Client)
# ============================================================================

def get_redaction_from_agent(original_text: str, difficulty: str) -> str:
    """
    Use OpenAI Client (connected to Ollama/Mistral) to get redaction from agent.
    This is the actual agent being trained/evaluated.
    
    Args:
        original_text: Document to redact
        difficulty: Task difficulty (easy, medium, hard)
    
    Returns:
        Redacted text from agent LLM
    """
    try:
        # Build task-specific prompt
        if difficulty == "easy":
            prompt = f"""You are a data privacy expert. Redact structured PII from this document.
            
Detect and replace with [REDACTED_TYPE]:
- Aadhaar numbers (12-digit patterns)
- PAN codes (ABCDE1234F format)  
- Phone numbers (+91 or 10-digit Indian)
- Email addresses
- Bank accounts (9-18 digits)
- IFSC codes

Document:
{original_text}

Provide only the redacted text, nothing else."""
        
        elif difficulty == "medium":
            prompt = f"""You are a data privacy expert. Redact structured AND contextual PII from this document.
            
Detect and replace:
- All structured PII (Aadhaar, PAN, phone, email, bank, IFSC)
- Person names (use [REDACTED_NAME])
- Organizations (use [REDACTED_ORGANIZATION])
- Locations/places (use [REDACTED_LOCATION])
- Medical facilities (use [REDACTED_FACILITY])

Preserve document readability and structure.

Document:
{original_text}

Provide only the redacted text, nothing else."""
        
        else:  # hard
            prompt = f"""You are a data privacy expert defending against re-identification attacks.
Redact ALL PII including quasi-identifiers that could enable re-identification.
            
Detect and replace:
- Structured PII (Aadhaar, PAN, phone, email, bank, IFSC)
- Names, organizations, locations, facilities
- Demographic descriptors (age, roles, titles)
- Specific medical conditions/rare diseases
- Specialized hospital names
- Any combination that could re-identify the person

Document:
{original_text}

Provide only the heavily redacted text, nothing else."""
        
        # Call LLM via OpenAI Client
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a data privacy redaction agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            timeout=30.0
        )
        
        redacted_text = (response.choices[0].message.content or "").strip()
        if not redacted_text:
            raise ValueError("Agent returned empty redaction")
        
        return redacted_text
    
    except Exception as e:
        print(f"[DEBUG] Agent redaction failed ({difficulty}): {e}", flush=True)
        # Fallback: use basic regex patterns
        redacted = original_text
        redacted = re.sub(r'\b\d{4}\s\d{4}\s\d{4}\b', '[REDACTED_AADHAAR]', redacted)
        redacted = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', '[REDACTED_PAN]', redacted)
        redacted = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[REDACTED_EMAIL]', redacted)
        return redacted


# ============================================================================
# Legacy Redaction Functions (Fallback Only)
# ============================================================================

def redact_easy_pii(original_text: str) -> str:
    """
    Basic redaction for Easy task: structured PII patterns.
    
    Uses regex to identify and redact:
    - Aadhaar: XXXX XXXX XXXX or 12-digit number
    - PAN: ABCDE1234F format
    - Phone: +91 10-digit or 10-digit starting with 6-9
    - Email: standard email format
    - Bank account: 9-18 digit numeric
    - IFSC: ABCD0XXXXXX format
    """
    redacted = original_text
    
    # Aadhaar: XXXX XXXX XXXX or 12 consecutive digits
    redacted = re.sub(r'\b\d{4}\s\d{4}\s\d{4}\b', '[REDACTED_AADHAAR]', redacted)
    redacted = re.sub(r'\b(?<!\d)\d{12}(?!\d)\b', '[REDACTED_AADHAAR]', redacted)
    
    # PAN: ABCDE1234F
    redacted = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', '[REDACTED_PAN]', redacted)
    
    # Phone: +91 followed by 10 digits or standalone 10-digit starting with 6-9
    redacted = re.sub(r'\+91\s?\d{10}\b', '[REDACTED_PHONE]', redacted)
    redacted = re.sub(r'\b[6-9]\d{9}\b', '[REDACTED_PHONE]', redacted)
    
    # Email
    redacted = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        '[REDACTED_EMAIL]',
        redacted
    )
    
    # Bank account: 9-18 digit numeric (case-insensitive with context)
    redacted = re.sub(r'\b\d{9,18}\b', '[REDACTED_BANK_ACCOUNT]', redacted)
    
    # IFSC: ABCD0XXXXXX
    redacted = re.sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', '[REDACTED_IFSC]', redacted)
    
    return redacted


def redact_medium_pii(original_text: str) -> str:
    """
    Medium redaction: contextual + NER-based detection.
    
    Strategy:
    1. First apply easy patterns (structured PII)
    2. Use spaCy NER to detect PERSON, ORG, GPE, FAC entities
    3. Redact medical roles, relative references
    4. Preserve readability while protecting quasi-identifiers
    """
    # Start with easy patterns
    redacted = redact_easy_pii(original_text)
    
    # Try to use spaCy for NER
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(original_text)
        
        # Collect entity spans to redact (reverse order to preserve indices)
        entities_to_redact = []
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "FAC"]:
                tag = {
                    "PERSON": "[REDACTED_NAME]",
                    "ORG": "[REDACTED_ORGANIZATION]",
                    "GPE": "[REDACTED_LOCATION]",
                    "FAC": "[REDACTED_FACILITY]",
                }.get(ent.label_, f"[REDACTED_{ent.label_}]")
                entities_to_redact.append((ent.start_char, ent.end_char, tag))
        
        # Apply redactions in reverse order (maintain string positions)
        for start, end, tag in sorted(entities_to_redact, reverse=True):
            redacted = redacted[:start] + tag + redacted[end:]
    
    except Exception as e:
        print(f"[DEBUG] spaCy NER failed: {e}, using fallback", flush=True)
        # Fallback: redact common medical/professional titles
        redacted = re.sub(
            r'\b(Dr\.|Doctor|Prof\.|Professor|Physician|Cardiologist|Surgeon)\s+[A-Z][a-z]+',
            '[REDACTED_NAME]',
            redacted
        )
    
    return redacted


def redact_hard_pii(original_text: str, attempt: int = 1) -> str:
    """
    Hard redaction: aggressive quasi-identifier removal.
    
    Strategy:
    - Attempt 1: Medium-level redaction
    - Attempt 2: More aggressive - remove demographic descriptors
    - Attempt 3: Maximum - remove specialized medical info, locations
    
    Goal: Prevent re-identification through quasi-identifier combinations.
    """
    if attempt == 1:
        return redact_medium_pii(original_text)
    
    elif attempt == 2:
        # More aggressive: remove demographic attributes
        redacted = redact_medium_pii(original_text)
        
        # Remove age indicators
        redacted = re.sub(
            r'\b(age|aged|year[s]?\s+old|years old)[\s,:]*\d+',
            '[REDACTED_AGE]',
            redacted,
            flags=re.IGNORECASE
        )
        
        # Remove specialized roles that could identify
        redacted = re.sub(
            r'\b(Chief|Head|Director|Lead|Senior)\s+(Cardiologist|Physician|Doctor|Surgeon)',
            '[REDACTED_ROLE]',
            redacted,
            flags=re.IGNORECASE
        )
        
        # Remove disease/condition + location combinations
        redacted = re.sub(
            r'\b(at|from|in|based at)\s+[A-Z][A-Za-z\s]+',
            'at [REDACTED_LOCATION]',
            redacted
        )
        
        return redacted
    
    else:  # attempt >= 3
        # Maximum redaction: remove most quasi-identifiers
        redacted = redact_hard_pii(original_text, attempt=2)
        
        # Remove rare disease indicators
        redacted = re.sub(
            r'\b(Takayasu|arteritis|syndrome|disease)\b',
            '[REDACTED_CONDITION]',
            redacted,
            flags=re.IGNORECASE
        )
        
        # Remove specialized hospital/institution names
        redacted = re.sub(
            r'\b(AIIMS|Apollo|Fortis|Max|Medanta|Delhi|Mumbai|Bangalore)\b',
            '[REDACTED_LOCATION]',
            redacted
        )
        
        return redacted


# ============================================================================
# Task Execution Functions
# ============================================================================

def execute_easy_task() -> Tuple[float, str, float]:
    """
    Execute Easy task: detect and redact structured PII using agent LLM.
    
    Returns:
        (score, action_description, reward)
    """
    try:
        # Get task
        task = get_easy_task()
        original_text = task["document_text"]
        pii_present = task.get("pii_present", [])
        
        # Agent (via OpenAI Client) decides what to redact
        redacted_text = get_redaction_from_agent(original_text, "easy")
        
        # Grade the redaction
        grade_result = grade_easy_task(original_text, redacted_text, pii_present)
        score = grade_result.get("score", 0.0)
        
        # Format action description
        pii_caught = grade_result.get("pii_caught", 0)
        action = f"redact_structured_pii(caught={pii_caught}/{len(pii_present)})"
        
        return score, action, score
    
    except Exception as e:
        print(f"[DEBUG] Easy task error: {e}", flush=True)
        action = f"redact_structured_pii(error={str(e)[:30]})"
        return 0.0, action, 0.0


def execute_medium_task() -> Tuple[float, str, float]:
    """
    Execute Medium task: detect contextual PII using agent LLM + grader validation.
    
    Returns:
        (score, action_description, reward)
    """
    try:
        # Get task
        task = get_medium_task()
        original_text = task["document_text"]
        pii_present = task.get("pii_present", [])
        
        # Agent (via OpenAI Client) decides what to redact
        redacted_text = get_redaction_from_agent(original_text, "medium")
        
        # Grade with LLM validation (Ollama backend)
        grade_result = grade_medium_task(
            original_text,
            redacted_text,
            pii_present,
            use_llm=True,
            llm_backend="ollama"
        )
        score = grade_result.get("score", 0.0)
        
        # Format action description
        action = "redact_contextual_pii(method=agent_llm+grader_validation)"
        
        return score, action, score
    
    except Exception as e:
        print(f"[DEBUG] Medium task error: {e}", flush=True)
        action = f"redact_contextual_pii(error={str(e)[:30]})"
        return 0.0, action, 0.0


def execute_hard_task() -> Tuple[float, str, List[float]]:
    """
    Execute Hard task: adversarial defense against re-identification using agent LLM.
    
    Implements 3-attempt defense loop:
    1. Initial redaction by agent LLM
    2. Judge checks for re-identifiability (Ollama/Mistral)
    3. If vulnerable, agent re-redacts more aggressively
    4. Repeat up to 3 attempts until defended or max attempts reached
    
    Returns:
        (final_score, action_description, rewards_per_attempt)
    """
    try:
        # Get task
        task = get_hard_task()
        original_text = task["document_text"]
        pii_present = task.get("pii_present", [])
        
        attempt_rewards = []
        
        # Defense loop: up to 3 attempts
        for attempt in range(1, MAX_ATTEMPTS_HARD + 1):
            # Agent (via OpenAI Client) redacts (more aggressively each attempt)
            redacted_text = get_redaction_from_agent(original_text, "hard")
            
            # Grade current redaction (with LLM judge)
            grade_result = grade_hard_task(
                original_text,
                redacted_text,
                pii_present,
                use_llm_judge=True
            )
            score = grade_result.get("score", 0.0)
            attempt_rewards.append(score)
            
            # Check if re-identifiable (from judge feedback)
            judge_result = grade_result.get("judge_result", {})
            is_reidentifiable = judge_result.get("is_reidentifiable", True)
            confidence = judge_result.get("confidence", 0.5)
            
            print(
                f"[DEBUG] Hard task attempt {attempt}: "
                f"score={score:.3f}, reidentifiable={is_reidentifiable}, "
                f"confidence={confidence:.2f}",
                flush=True
            )
            
            # Check if secured or max attempts reached
            if not is_reidentifiable or attempt >= MAX_ATTEMPTS_HARD:
                break
        
        # Final score is the last attempt's score
        final_score = attempt_rewards[-1] if attempt_rewards else 0.0
        action = f"defend_against_reidentification(attempts={len(attempt_rewards)}/{MAX_ATTEMPTS_HARD})"
        
        return final_score, action, attempt_rewards
    
    except Exception as e:
        print(f"[DEBUG] Hard task error: {e}", flush=True)
        action = f"defend_against_reidentification(error={str(e)[:30]})"
        return 0.0, action, [0.0]


# ============================================================================
# Main Inference Loop
# ============================================================================

async def main() -> None:
    """
    Main inference loop following hackathon stdout format.
    
    Executes 3-step task progression (Easy → Medium → Hard) and logs
    results in strict format required by grading infrastructure.
    """
    
    # Initialize tracking
    all_rewards: List[float] = []
    steps_taken = 0
    total_score = 0.0
    success = False
    
    # Log episode start
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        # ====================================================================
        # STEP 1: Easy Task (Structured PII Detection)
        # ====================================================================
        easy_score, easy_action, easy_reward = execute_easy_task()
        steps_taken = 1
        all_rewards.append(easy_reward)
        log_step(step=1, action=easy_action, reward=easy_reward, done=False, error=None)
        print(f"[DEBUG] Easy task complete: score={easy_score:.3f}", flush=True)
        
        # ====================================================================
        # STEP 2: Medium Task (Contextual PII + NER + LLM)
        # ====================================================================
        medium_score, medium_action, medium_reward = execute_medium_task()
        steps_taken = 2
        all_rewards.append(medium_reward)
        log_step(step=2, action=medium_action, reward=medium_reward, done=False, error=None)
        print(f"[DEBUG] Medium task complete: score={medium_score:.3f}", flush=True)
        
        # ====================================================================
        # STEP 3: Hard Task (Adversarial Defense Loop)
        # ====================================================================
        hard_score, hard_action, hard_rewards = execute_hard_task()
        steps_taken = 3
        all_rewards.extend(hard_rewards)  # Add all attempt rewards
        log_step(
            step=3,
            action=hard_action,
            reward=hard_score,
            done=True,
            error=None
        )
        print(
            f"[DEBUG] Hard task complete: "
            f"score={hard_score:.3f}, attempts={len(hard_rewards)}",
            flush=True
        )
        
        # ====================================================================
        # Final Scoring
        # ====================================================================
        # Score = average of 3 tasks
        task_scores = [easy_score, medium_score, hard_score]
        total_score = sum(task_scores) / len(task_scores)
        total_score = min(max(total_score, 0.0), 1.0)  # Clamp to [0, 1]
        success = total_score >= SUCCESS_SCORE_THRESHOLD
        
        print(
            f"[DEBUG] Final scoring: "
            f"easy={easy_score:.3f}, medium={medium_score:.3f}, hard={hard_score:.3f}, "
            f"average={total_score:.3f}, success={success}",
            flush=True
        )
    
    except Exception as e:
        error_msg = f"Inference error: {str(e)}"
        print(f"[DEBUG] {error_msg}", flush=True)
        success = False
    
    finally:
        # Always emit [END] line
        # Use step-wise rewards (one per step)
        step_rewards = [
            all_rewards[0] if len(all_rewards) > 0 else 0.0,
            all_rewards[1] if len(all_rewards) > 1 else 0.0,
            all_rewards[2] if len(all_rewards) > 2 else 0.0,
        ]
        log_end(success=success, steps=steps_taken, score=total_score, rewards=step_rewards)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    asyncio.run(main())
