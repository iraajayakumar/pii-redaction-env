import asyncio
import os
import textwrap
from typing import List, Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    from pii_redaction_env.client import PiiRedactionEnv
    from pii_redaction_env.models import PiiRedactionAction
except ImportError:
    from client import PiiRedactionEnv
    from models import PiiRedactionAction


API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "HuggingFaceH4/zephyr-7b-beta")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")

TASKS = ["easy", "medium", "hard"]
BENCHMARK = "pii_redaction_env"
MAX_HARD_STEPS = 3
SUCCESS_SCORE_THRESHOLD = 0.5
TEMPERATURE = 0.2
MAX_TOKENS = 1800


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def truncate_action(action_str: str, max_len: int = 120) -> str:
    flat = " ".join(action_str.split())
    if len(flat) > max_len:
        return flat[: max_len - 3] + "..."
    return flat


def build_prompt(task_name: str, document_text: str, prior_feedback: str = "", attempt: int = 1) -> str:
    if task_name == "easy":
        instructions = """
Redact all structured Indian PII from the document.

Use only these exact tags when appropriate:
[REDACTED_AADHAAR]
[REDACTED_PAN]
[REDACTED_PHONE]
[REDACTED_EMAIL]
[REDACTED_BANK_ACCOUNT]
[REDACTED_IFSC]

Rules:
- Replace PII with the correct tag.
- Do not delete content.
- Preserve document structure.
- Return only the redacted document text.
""".strip()
    elif task_name == "medium":
        instructions = """
Redact all direct and contextual PII from the document.

Use only these exact tags when appropriate:
[REDACTED_NAME]
[REDACTED_ORGANIZATION]
[REDACTED_ADDRESS]
[REDACTED_PHONE]
[REDACTED_EMAIL]
[REDACTED_DOB]
[REDACTED_RELATIVE_REFERENCE]

Rules:
- Replace PII with the correct tag.
- Preserve document structure and readability.
- Redact contextual references that can identify a person.
- Return only the redacted document text.
""".strip()
    else:
        instructions = f"""
Redact the document to prevent re-identification under a hard privacy setting.

Attempt number: {attempt}

Rules:
- Aggressively redact direct identifiers, quasi-identifiers, contextual identifiers, and linkable details.
- Preserve document structure as much as possible.
- Use appropriate redaction tags already present in the task when possible.
- Return only the redacted document text.

Prior feedback:
{prior_feedback or "None"}
""".strip()

    return textwrap.dedent(
        f"""
        {instructions}

        Document:
        {document_text}
        """
    ).strip()


def get_agent_redaction(
    client: OpenAI,
    task_name: str,
    document_text: str,
    prior_feedback: str = "",
    attempt: int = 1,
) -> str:
    user_prompt = build_prompt(task_name, document_text, prior_feedback, attempt)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are an automated Data Privacy Officer redacting Indian documents under the DPDP Act 2023.",
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else document_text
    except Exception:
        return document_text


async def run_single_task(client: OpenAI, task_name: str) -> tuple[int, List[float], float, bool]:
    os.environ["TASK_TYPE"] = task_name
    env = PiiRedactionEnv(base_url=ENV_BASE_URL)

    rewards: List[float] = []
    steps_taken = 0
    final_score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        observation = await env.reset()
        current_text = observation.document_text
        feedback = ""

        max_steps = 1 if task_name in ("easy", "medium") else MAX_HARD_STEPS

        for step in range(1, max_steps + 1):
            action_text = get_agent_redaction(
                client=client,
                task_name=task_name,
                document_text=current_text,
                prior_feedback=feedback,
                attempt=step,
            )

            next_obs, reward, done, info = await env.step(
                PiiRedactionAction(
                    redacted_text=action_text,
                    identified_pii_types=[],
                    reasoning="",
                )
            )

            reward = max(0.0, min(1.0, float(reward or 0.0)))
            rewards.append(reward)
            steps_taken = step

            error = info.get("error") if isinstance(info, dict) else None
            log_step(
                step=step,
                action=truncate_action(action_text),
                reward=reward,
                done=done,
                error=error,
            )

            feedback = next_obs.instructions or ""
            current_text = next_obs.document_text or action_text

            if done:
                break

        final_score = rewards[-1] if rewards else 0.0
        success = final_score >= SUCCESS_SCORE_THRESHOLD
        return steps_taken, rewards, final_score, success

    finally:
        try:
            await env.close()
        finally:
            log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    for task_name in TASKS:
        await run_single_task(client, task_name)


if __name__ == "__main__":
    asyncio.run(main())