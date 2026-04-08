---
title: PII Redaction Environment
emoji: 🔐
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - privacy
  - pii
  - compliance
  - rl
---

# PII Redaction Environment

An OpenEnv environment for training and evaluating AI agents to redact personally identifiable information (PII) from documents under the Data Protection laws (DPDP Act 2023 - India).

## Overview

**Real-World Task:** Automated data privacy compliance. Organizations must redact sensitive information from documents for GDPR/HIPAA/DPDP compliance. This environment trains agents to identify and redact:
- **Structured PII** (Aadhaar, PAN, phone, email, bank accounts, IFSC codes)
- **Contextual PII** (names, organizations, locations in medical/legal contexts)
- **Quasi-Identifiers** (age, roles, rare conditions) that could enable re-identification

## Environment Description

### Task Difficulty Progression

The environment provides **3 tasks with increasing difficulty**:

#### **Task 1: Easy** (Structured PII Detection)
- **Objective:** Detect and redact structured PII using pattern matching
- **Difficulty:** Easy
- **PII Types:** Aadhaar numbers, PAN codes, phone numbers, emails, bank accounts, IFSC codes
- **Agent Strategy:** Regex-based pattern detection
- **Expected Score:** 0.80-1.00 (high success rate)
- **Sample Document:** Indian banking/government documents with explicit identifiers

#### **Task 2: Medium** (Contextual PII + Semantic Understanding)
- **Objective:** Detect contextual PII that requires semantic understanding
- **Difficulty:** Medium  
- **PII Types:** Person names, organizations, locations, medical facilities, job titles in context
- **Agent Strategy:** Named Entity Recognition (NER) + LLM-based validation (Mistral)
- **Expected Score:** 0.65-0.85 (requires context understanding)
- **Sample Document:** Medical reports, legal documents with implicit person/org references

#### **Task 3: Hard** (Adversarial De-anonymization Defense)
- **Objective:** Defend against re-identification attacks using quasi-identifiers
- **Difficulty:** Hard
- **Challenge:** Grader attempts re-identification using combination of quasi-identifiers
- **Defense Loop:** Agent gets 3 attempts to redact aggressively enough to prevent re-identification
- **Agent Strategy:** LLM-guided aggressive redaction with iterative feedback
- **Expected Score:** 0.50-0.75 (high difficulty, requires aggressive redaction)
- **Sample Document:** Medical/legal documents with quasi-identifiers (age, rare conditions, specialized roles, locations)

---

## Action & Observation Spaces

### Action Space

**Type:** `PiiRedactionAction` (Pydantic model)

```python
class PiiRedactionAction(BaseModel):
    redacted_text: str  # Document with PII redacted (required)
```

**Description:**
- Agent receives original document text
- Agent returns redacted version with PII replaced with `[REDACTED_TYPE]` tokens
- No explicit action parameters - the entire redacted document is the action

---

### Observation Space

**Type:** `PiiRedactionObservation` (Pydantic model)

```python
class PiiRedactionObservation(BaseModel):
    task_id: str                    # "easy", "medium", or "hard"
    original_text: str              # Original document
    redacted_text: str              # Agent's redacted version
    score: float                    # Grader score [0.0, 1.0]
    pii_caught: int                 # Number of PII instances successfully redacted
    pii_total: int                  # Total PII instances in document
    judge_result: Optional[Dict]    # For hard task: re-identification assessment
    feedback: str                   # Human-readable feedback
```

**Score Interpretation:**
- **1.0:** Perfect redaction (all PII redacted, no over-redaction)
- **0.8:** Good redaction (most PII caught, minimal data loss)
- **0.5:** Adequate redaction (significant PII redacted but some risk)
- **0.2:** Poor redaction (critical PII exposed, re-identification possible)
- **0.0:** Failed (PII fully exposed or no redaction attempted)

---

### Reward Function

**Scoring Strategy:**

```
easy_score = (pii_caught / pii_total) × reduction_penalty
  where reduction_penalty penalizes over-aggressive redaction (>50% loss)

medium_score = (pii_caught / pii_total) × context_quality
  where context_quality is LLM assessment of semantic preservation

hard_score = defense_effectiveness
  = 0.5 × baseline_score + 0.5 × (successful_defenses / max_attempts)
```

**Final Episode Score:**
```
episode_score = (easy_score + medium_score + hard_score) / 3
  clamped to [0.0, 1.0]
```

**Success Threshold:** `score >= 0.5`

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- Docker (for container deployment)
- Ollama + Mistral-7B (for LLM grading, local inference only)

### Local Installation

```bash
# Clone repository
git clone https://github.com/iraajayakumar/pii-redaction-env
cd pii_redaction_env

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r pii_redaction_env/server/requirements.txt
pip install openai

# Verify installation
openenv validate
```

### Environment Variables

```bash
# Required for LLM-based grading/inference
export API_BASE_URL="http://localhost:11434"      # Ollama endpoint
export MODEL_NAME="mistral"                        # Model to use
export HF_TOKEN="your-huggingface-token"          # Optional, for HuggingFace API fallback
```

### Running Locally

```bash
# Start Ollama (in separate terminal)
ollama serve

# In another terminal, pull Mistral model
ollama pull mistral

# Run baseline inference
cd pii_redaction_env
python inference.py
```

**Expected Output:**
```
[START] task=pii_redaction env=pii_redaction_env model=mistral
[STEP] step=1 action=redact_structured_pii(caught=10/10) reward=0.92 done=false error=null
[STEP] step=2 action=redact_contextual_pii(method=agent_llm+grader_validation) reward=0.71 done=false error=null
[STEP] step=3 action=defend_against_reidentification(attempts=2/3) reward=0.68 done=true error=null
[END] success=true steps=3 score=0.77 rewards=0.92,0.71,0.68
```

### Docker Deployment

```bash
# Build Docker image
cd pii_redaction_env
docker build -t pii-redaction:latest .

# Run container
docker run -e API_BASE_URL="http://localhost:11434" \
           -e MODEL_NAME="mistral" \
           -p 8000:8000 \
           pii-redaction:latest
```

### Deploy to Hugging Face Spaces

```bash
# Ensure you're logged in
huggingface-cli login

# Create Space on Hugging Face (via web UI)
# Then clone and push:
git clone https://huggingface.co/spaces/YOUR_USERNAME/pii-redaction-env
cd pii-redaction-env
cp -r ../pii_redaction_env/* .
git add .
git commit -m "Initial deployment"
git push
```

---

## Baseline Scores

**Baseline Agent:** Mistral-7B with structured prompting

| Task | Score | Strategy |
|------|-------|----------|
| Easy | 0.92 | Regex pattern + spaCy NER |
| Medium | 0.71 | NER + LLM validation (Mistral) |
| Hard | 0.68 | 2-attempt iterative defense + quasi-ID removal |
| **Overall** | **0.77** | Average of 3 tasks |

**Note:** Scores vary based on document complexity. Hard task shows improvement with iterative feedback from re-identification judge.

---

## Testing

### Quick Test
```bash
python test_quick_judges.py
```

### Full Integration Test
```bash
python test_llm_judges_integrated.py
```

### All Tasks Comprehensive Test
```bash
python test_all_tasks_comprehensive.py
```

---

## File Structure

```
pii_redaction_env/
├── inference.py                      # Baseline agent + evaluation loop
├── openenv.yaml                      # OpenEnv spec
├── Dockerfile                        # Docker container definition
├── README.md                         # This file
├── server/
│   ├── app.py                       # FastAPI server
│   ├── requirements.txt              # Python dependencies
│   ├── tasks/
│   │   ├── easy.py                  # Easy task generator
│   │   ├── medium.py                # Medium task generator
│   │   └── hard.py                  # Hard task generator
│   ├── graders/
│   │   ├── easy_grader.py           # Easy task grader (regex)
│   │   ├── medium_grader.py         # Medium task grader (NER + LLM)
│   │   └── hard_grader.py           # Hard task grader (LLM judge)
│   └── data/
│       └── documents.py             # Professional sample documents
└── tests/
    ├── test_quick_judges.py         # Fast grader tests
    └── test_llm_judges_integrated.py # Full integration tests
```

---

## API Reference

### Reset Environment
```python
from pii_redaction_env import PiiRedactionEnv

env = await PiiRedactionEnv.from_docker_image("pii-redaction:latest")
observation = await env.reset()
# Returns: PiiRedactionObservation with task_id, original_text
```

### Execute Step
```python
from pii_redaction_env import PiiRedactionAction

action = PiiRedactionAction(redacted_text="...redacted document...")
result = await env.step(action)
# Returns: (observation, reward, done, info)
```

### Get Environment State
```python
state = await env.state()
# Returns: Current environment state snapshot
```

---

## Troubleshooting

**"Ollama not available" warning:**
- Ensure Ollama is running: `ollama serve`
- Check endpoint: `curl http://localhost:11434/api/tags`
- Falls back to mock judges automatically

**Inference timeout (>20 minutes):**
- Mistral inference takes ~2-5 min per task
- Ensure sufficient resources (2+ vCPU, 8GB RAM)
- For faster iteration, set `use_llm_judge=False` in graders

**OpenEnv validation fails:**
- Run: `openenv validate` from `pii_redaction_env/` directory
- Check `openenv.yaml` exists with proper structure
- Verify all imports in Python files work

---

## Citation

If you use this environment in research, please cite:

```bibtex
@misc{pii_redaction_env,
  title={PII Redaction Environment: Training Agents for Privacy Compliance},
  author={Jayakumar, Iraa},
  year={2026},
  howpublished={\url{https://github.com/iraajayakumar/pii-redaction-env}}
}
```

---

## License

MIT License - See LICENSE file for details

- Authenticate with Hugging Face: The command will prompt for login if not already authenticated

### Options

- `--directory`, `-d`: Directory containing the OpenEnv environment (defaults to current directory)
- `--repo-id`, `-r`: Repository ID in format 'username/repo-name' (defaults to 'username/env-name' from openenv.yaml)
- `--base-image`, `-b`: Base Docker image to use (overrides Dockerfile FROM)
- `--private`: Deploy the space as private (default: public)

### Examples

```bash
# Push to your personal namespace (defaults to username/env-name from openenv.yaml)
openenv push

# Push to a specific repository
openenv push --repo-id my-org/my-env

# Push with a custom base image
openenv push --base-image ghcr.io/meta-pytorch/openenv-base:latest

# Push as a private space
openenv push --private

# Combine options
openenv push --repo-id my-org/my-env --base-image custom-base:latest --private
```

After deployment, your space will be available at:
`https://huggingface.co/spaces/<repo-id>`

The deployed space includes:
- **Web Interface** at `/web` - Interactive UI for exploring the environment
- **API Documentation** at `/docs` - Full OpenAPI/Swagger interface
- **Health Check** at `/health` - Container health monitoring
- **WebSocket** at `/ws` - Persistent session endpoint for low-latency interactions

## Environment Details

### Action
**PiiRedactionAction**: Contains a single field
- `message` (str) - The message to echo back

### Observation
**PiiRedactionObservation**: Contains the echo response and metadata
- `echoed_message` (str) - The message echoed back
- `message_length` (int) - Length of the message
- `reward` (float) - Reward based on message length (length × 0.1)
- `done` (bool) - Always False for echo environment
- `metadata` (dict) - Additional info like step count

### Reward
The reward is calculated as: `message_length × 0.1`
- "Hi" → reward: 0.2
- "Hello, World!" → reward: 1.3
- Empty message → reward: 0.0

## Advanced Usage

### Connecting to an Existing Server

If you already have a Pii Redaction Env environment server running, you can connect directly:

```python
from pii_redaction_env import PiiRedactionEnv

# Connect to existing server
pii_redaction_envenv = PiiRedactionEnv(base_url="<ENV_HTTP_URL_HERE>")

# Use as normal
result = pii_redaction_envenv.reset()
result = pii_redaction_envenv.step(PiiRedactionAction(message="Hello!"))
```

Note: When connecting to an existing server, `pii_redaction_envenv.close()` will NOT stop the server.

### Using the Context Manager

The client supports context manager usage for automatic connection management:

```python
from pii_redaction_env import PiiRedactionAction, PiiRedactionEnv

# Connect with context manager (auto-connects and closes)
with PiiRedactionEnv(base_url="http://localhost:8000") as env:
    result = env.reset()
    print(f"Reset: {result.observation.echoed_message}")
    # Multiple steps with low latency
    for msg in ["Hello", "World", "!"]:
        result = env.step(PiiRedactionAction(message=msg))
        print(f"Echoed: {result.observation.echoed_message}")
```

The client uses WebSocket connections for:
- **Lower latency**: No HTTP connection overhead per request
- **Persistent session**: Server maintains your environment state
- **Efficient for episodes**: Better for many sequential steps

### Concurrent WebSocket Sessions

The server supports multiple concurrent WebSocket connections. To enable this,
modify `server/app.py` to use factory mode:

```python
# In server/app.py - use factory mode for concurrent sessions
app = create_app(
    PiiRedactionEnvironment,  # Pass class, not instance
    PiiRedactionAction,
    PiiRedactionObservation,
    max_concurrent_envs=4,  # Allow 4 concurrent sessions
)
```

Then multiple clients can connect simultaneously:

```python
from pii_redaction_env import PiiRedactionAction, PiiRedactionEnv
from concurrent.futures import ThreadPoolExecutor

def run_episode(client_id: int):
    with PiiRedactionEnv(base_url="http://localhost:8000") as env:
        result = env.reset()
        for i in range(10):
            result = env.step(PiiRedactionAction(message=f"Client {client_id}, step {i}"))
        return client_id, result.observation.message_length

# Run 4 episodes concurrently
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_episode, range(4)))
```

## Development & Testing

### Direct Environment Testing

Test the environment logic directly without starting the HTTP server:

```bash
# From the server directory
python3 server/pii_redaction_env_environment.py
```

This verifies that:
- Environment resets correctly
- Step executes actions properly
- State tracking works
- Rewards are calculated correctly

### Running Locally

Run the server locally for development:

```bash
uvicorn server.app:app --reload
```

## Project Structure

```
pii_redaction_env/
├── .dockerignore         # Docker build exclusions
├── __init__.py            # Module exports
├── README.md              # This file
├── openenv.yaml           # OpenEnv manifest
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependencies (generated)
├── client.py              # PiiRedactionEnv client
├── models.py              # Action and Observation models
└── server/
    ├── __init__.py        # Server module exports
    ├── pii_redaction_env_environment.py  # Core environment logic
    ├── app.py             # FastAPI application (HTTP + WebSocket endpoints)
    └── Dockerfile         # Container image definition
```
