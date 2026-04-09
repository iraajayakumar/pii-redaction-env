"""
Inference Script for PII Redaction Environment
===============================================

ENVIRONMENT VARIABLES (for HF Space execution):
    HF_TOKEN           Your HuggingFace API key (for LLM calls)
    API_BASE_URL       LLM endpoint (default: https://router.huggingface.co/v1)
    MODEL_NAME         LLM model ID (default: HuggingFaceH4/zephyr-7b-beta)
    ENV_BASE_URL       Environment server URL (default: http://localhost:8000)

STDOUT FORMAT (Hackathon Compliance):
- [START] task=pii_redaction env=pii_redaction_env model=<model_name>
- [STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
- [END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

Task Progression (3 steps):
1. Easy: Detect structured PII (Aadhaar, PAN, phone, email, bank, IFSC)
2. Medium: Contextual + implicit PII detection with NER + LLM validation
3. Hard: Adversarial defense (3 attempts to prevent re-identification)

Final Score = Average of (easy_score, medium_score, hard_score) ∈ [0, 1]

NOTE: This script runs inside HF Space and connects to the environment server via HTTP.
"""

import asyncio
import os
import textwrap
from typing import List, Optional

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import OpenEnv client and action types
try:
    # Try absolute imports first (when running as module)
    from pii_redaction_env.client import PiiRedactionEnv
    from pii_redaction_env.models import PiiRedactionAction
except ImportError:
    try:
        # Try relative imports (when running as script)
        from client import PiiRedactionEnv
        from models import PiiRedactionAction
    except ImportError as e:
        print(f"[DEBUG] Import error: {e}", flush=True)
        print(f"[DEBUG] Make sure client.py and models.py are in the same directory", flush=True)
        exit(1)

# Environment variables (STRICT access for validator requirements)
# Validator injects: API_BASE_URL (proxy URL), API_KEY (authentication)
# MUST use os.environ[] strictly to guarantee validator's values are used
try:
    # Strict access - use EXACTLY what validator injected
    API_BASE_URL = os.environ["API_BASE_URL"]
    API_KEY = os.environ["API_KEY"]
except KeyError:
    # Local testing fallback only
    API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
    API_KEY = os.getenv("API_KEY") or os.getenv("HF_TOKEN", "")

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "HuggingFaceH4/zephyr-7b-beta")

# Initialize OpenAI client with VALIDATOR'S credentials
client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY, timeout=60.0)

# Task configuration
TASK_NAME = "pii_redaction"
BENCHMARK = "pii_redaction_env"
SUCCESS_SCORE_THRESHOLD = 0.5
MIN_SCORE = 0.01  # Validator requires scores strictly in (0, 1), not endpoints
MAX_SCORE = 0.99  # Clamp to ensure scores never equal 0.0 or 1.0

# Logging Functions (Hackathon Compliance)
def log_start(task: str, env: str, model: str) -> None:
    """Log episode start."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    """Log step execution."""
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """Log episode completion."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success_val = str(success).lower()
    print(f"[END] success={success_val} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def truncate_action(action_str: str, max_len: int = 100) -> str:
    """Truncate action string for logging."""
    if len(action_str) > max_len:
        return action_str[:max_len-3] + "..."
    return action_str


def get_agent_redaction(original_text: str, difficulty: str) -> str:
    """Get redaction from LLM agent via OpenAI client."""
    
    if difficulty == "easy":
        prompt = f"""Redact structured PII: Aadhaar, PAN, phone, email, bank account, IFSC.
Replace with [REDACTED_TYPE].

Document:
{original_text}

Return only the redacted text."""
    elif difficulty == "medium":
        prompt = f"""Redact structured + contextual PII: names, organizations, locations, facilities.
Use [REDACTED_NAME], [REDACTED_ORGANIZATION], [REDACTED_LOCATION], [REDACTED_FACILITY].

Document:
{original_text}

Return only the redacted text."""
    else:  # hard
        prompt = f"""Aggressively redact ALL PII and quasi-identifiers to prevent re-identification.
Include: structured PII, names, orgs, locations, age, roles, conditions, hospitals.

Document:
{original_text}

Return only the heavily redacted text."""
    
    try:
        # Make the API call through the provided base_url and api_key
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a data privacy expert. Redact PII from documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            timeout=10.0
        )
        
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        # Log errors but still return something
        print(f"[DEBUG] Agent redaction error ({difficulty}): {type(e).__name__}: {e}", flush=True)
        # Return original text as fallback
        return original_text


# ============================================================================
# Main Inference Loop
# ============================================================================

async def main() -> None:
    """
    Main evaluation loop using OpenEnv client pattern.
    
    Flow:
    1. Initialize async environment for each task
    2. Reset → Get observation (task) → Step with agent action → Get outcome
    3. Agent uses LLM (OpenAI client) to redact document
    4. Environment grades redaction and returns reward
    5. Hard task includes multi-attempt defense loop
    6. Aggregate rewards and log results
    """
    log_start(TASK_NAME, BENCHMARK, MODEL_NAME)
    
    # CRITICAL: Verify LLM API is accessible through validator's proxy FIRST
    try:
        print(f"[DEBUG] Verifying LLM access with API_BASE_URL={API_BASE_URL}", flush=True)
        test_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Respond with 'ok'"}],
            temperature=0.3,
            max_tokens=10,
            timeout=5.0
        )
        print(f"[DEBUG] LLM verification OK - API credentials working", flush=True)
    except Exception as e:
        print(f"[DEBUG] LLM verification failed: {type(e).__name__}: {e}", flush=True)
        print(f"[DEBUG] API_BASE_URL={API_BASE_URL}, API_KEY={'***' if API_KEY else 'EMPTY'}", flush=True)
    
    all_rewards = []
    total_steps = 0
    
    try:
        # ====================================================================
        # EASY TASK: Structured PII Detection
        # ====================================================================
        env_easy = None
        try:
            print(f"[DEBUG] Connecting to environment at {ENV_BASE_URL}", flush=True)
            env_easy = PiiRedactionEnv(base_url=ENV_BASE_URL)
            observation = await env_easy.reset()
            
            original_text = observation.document_text
            print(f"[DEBUG] Easy task received document ({len(original_text)} chars)", flush=True)
            
            # Agent redaction via OpenAI client
            redacted_text = get_agent_redaction(original_text, "easy")
            
            # Environment step: grading happens inside environment
            # step() returns (observation, reward, done, info) tuple
            next_obs, reward, done, info = await env_easy.step(PiiRedactionAction(redacted_text=redacted_text))
            
            # Clamp score to strictly (0, 1) range
            reward = max(MIN_SCORE, min(MAX_SCORE, reward))
            all_rewards.append(reward)
            total_steps += 1
            
            action_desc = truncate_action(f"easy_pii_redaction({len(original_text)} chars)")
            log_step(total_steps, action_desc, reward, True, None)
            print(f"[DEBUG] Easy: reward={reward:.3f}", flush=True)
            
        except Exception as e:
            print(f"[DEBUG] Easy task error: {e}", flush=True)
            log_step(total_steps + 1, "easy_task_failed", MIN_SCORE, True, str(e)[:50])
            all_rewards.append(MIN_SCORE)
            total_steps += 1
        finally:
            if env_easy:
                await env_easy.close()
        
        # ====================================================================
        # MEDIUM TASK: Contextual PII + NER + LLM Validation
        # ====================================================================
        env_medium = None
        try:
            env_medium = PiiRedactionEnv(base_url=ENV_BASE_URL)
            observation = await env_medium.reset()
            
            original_text = observation.document_text
            print(f"[DEBUG] Medium task received document ({len(original_text)} chars)", flush=True)
            
            # Agent redaction via OpenAI client (with contextual awareness)
            redacted_text = get_agent_redaction(original_text, "medium")
            
            # Environment step: grading with NER validation
            # step() returns (observation, reward, done, info) tuple
            next_obs, reward, done, info = await env_medium.step(PiiRedactionAction(redacted_text=redacted_text))
            
            # Clamp score to strictly (0, 1) range
            reward = max(MIN_SCORE, min(MAX_SCORE, reward))
            all_rewards.append(reward)
            total_steps += 1
            
            action_desc = truncate_action(f"medium_pii_redaction({len(original_text)} chars)")
            log_step(total_steps, action_desc, reward, True, None)
            print(f"[DEBUG] Medium: reward={reward:.3f}", flush=True)
            
        except Exception as e:
            print(f"[DEBUG] Medium task error: {e}", flush=True)
            log_step(total_steps + 1, "medium_task_failed", MIN_SCORE, True, str(e)[:50])
            all_rewards.append(MIN_SCORE)
            total_steps += 1
        finally:
            if env_medium:
                await env_medium.close()
        
        # ====================================================================
        # HARD TASK: Adversarial Defense with Multi-Attempt Loop
        # ====================================================================
        env_hard = None
        try:
            env_hard = PiiRedactionEnv(base_url=ENV_BASE_URL)
            observation = await env_hard.reset()
            
            original_text = observation.document_text
            print(f"[DEBUG] Hard task received document ({len(original_text)} chars)", flush=True)
            
            # Defense loop: up to 3 attempts to prevent re-identification
            hard_reward = MIN_SCORE
            for attempt in range(1, 4):
                # Agent redaction (increasingly aggressive per attempt)
                redacted_text = get_agent_redaction(original_text, "hard")
                
                # Environment step: judge evaluates re-identifiability
                # step() returns (observation, reward, done, info) tuple
                next_obs, reward, done, info = await env_hard.step(PiiRedactionAction(redacted_text=redacted_text))
                
                # Clamp score to strictly (0, 1) range
                reward = max(MIN_SCORE, min(MAX_SCORE, reward))
                hard_reward = reward
                total_steps += 1
                
                action_desc = truncate_action(f"defend_attempt_{attempt}({len(original_text)} chars)")
                log_step(total_steps, action_desc, reward, done, None)
                
                print(f"[DEBUG] Hard attempt {attempt}: reward={reward:.3f}, done={done}", flush=True)
                
                # Break if passed or max attempts reached
                if done or attempt >= 3:
                    break
            
            all_rewards.append(hard_reward)
            print(f"[DEBUG] Hard: final_reward={hard_reward:.3f}", flush=True)
            
        except Exception as e:
            print(f"[DEBUG] Hard task error: {e}", flush=True)
            log_step(total_steps + 1, "hard_task_failed", MIN_SCORE, True, str(e)[:50])
            all_rewards.append(MIN_SCORE)
            total_steps += 1
        finally:
            if env_hard:
                await env_hard.close()
        
        # ====================================================================
        # Final Scoring
        # ====================================================================
        if all_rewards and len(all_rewards) >= 3:
            # Take first 3 rewards (one per task type)
            task_rewards = all_rewards[:3]
            episode_score = sum(task_rewards) / 3
        else:
            episode_score = MIN_SCORE
        
        # Clamp to strictly (0, 1) - validator requires scores NOT at endpoints
        episode_score = max(MIN_SCORE, min(MAX_SCORE, episode_score))
        
        # Success = score >= threshold
        is_success = episode_score >= SUCCESS_SCORE_THRESHOLD
        
        print(f"[DEBUG] Final: score={episode_score:.3f}, success={is_success}, steps={total_steps}", flush=True)
        
    except Exception as e:
        print(f"[ERROR] Main loop failed: {e}", flush=True)
        episode_score = 0.0
        is_success = False
        total_steps = 0
    
    # Log episode completion
    log_end(is_success, total_steps, episode_score, all_rewards[:3] if len(all_rewards) >= 3 else all_rewards)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[DEBUG] Interrupted by user", flush=True)
        log_end(False, 0, 0.0, [])
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        log_end(False, 0, 0.0, [])
        exit(1)
