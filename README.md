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

### Downstream Use Cases

This environment directly enables:

**1. Healthcare Organizations**
- De-identification of Electronic Health Records (EHRs) for research data sharing
- HIPAA-compliant document anonymization for audit trails
- Training agents to protect patient privacy while preserving medical context

**2. Legal/Compliance Teams**
- Automated redaction of contracts, court filings, and legal briefs before public release
- Preparation of documents for regulatory submissions (DPDP Act 2023, GDPR)
- Evaluation of redaction agent performance under Indian privacy law

**3. Financial Institutions**
- Customer document anonymization (KYC, loan applications) for ML training datasets
- Internal document sanitization for knowledge base systems
- Audit trail protection for compliance reporting

**4. RL/ML Research**
- Benchmark for evaluating LLM capabilities in nuanced privacy tasks
- Training environment for agents that must balance privacy with utility
- Study of reward shaping in safety-critical compliance scenarios
- Testing frontier models (GPT-4, Claude, etc.) on realistic privacy challenges

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
- **Agent Strategy:** Named Entity Recognition (NER) + LLM-based validation (HuggingFace)
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

- Python 3.10+
- Docker (for container deployment)
- HuggingFace account with read-only API token (for LLM grading)

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

Create a `.env` file in `pii_redaction_env/` with:

```bash
# LLM Backend Configuration (HuggingFace Inference API)
LLM_BACKEND=huggingface
HF_TOKEN=your-huggingface-read-only-token  # Get from https://huggingface.co/settings/tokens
HF_MODEL=HuggingFaceH4/zephyr-7b-beta      # Judge model (efficient 7B model)

# Agent Model (displayed in logs)
MODEL_NAME=zephyr-7b-beta

# Feature Flags
USE_LLM_VALIDATION=true
SENSITIVITY_PROFILE=default
```

**To get your HF token:**
1. Visit https://huggingface.co/settings/tokens
2. Create a new fine-grained read-only token
3. Accept the license for `HuggingFaceH4/zephyr-7b-beta` model

### Running Locally

```bash
# Set up environment variables
cp pii_redaction_env/.env.example pii_redaction_env/.env
# Edit .env and add your HF_TOKEN

# Run baseline inference
cd pii_redaction_env
python inference.py
```

### Docker Deployment

```bash
# Build Docker image
cd pii_redaction_env
docker build -t pii-redaction:latest .

# Run container
docker run -e HF_TOKEN="your-huggingface-token" \
           -e HF_MODEL="HuggingFaceH4/zephyr-7b-beta" \
           -e LLM_BACKEND="huggingface" \
           -p 8000:8000 \
           pii-redaction:latest
```

**Note:** HuggingFace API requires internet access. The environment pings `api-inference.huggingface.co`.

### Deploy to Hugging Face Spaces

This environment is already deployed to HuggingFace Spaces:
**[https://huggingface.co/spaces/iraajayakumar/pii-redaction-environment](https://huggingface.co/spaces/iraajayakumar/pii-redaction-environment)**

---

## Baseline Scores

**Baseline Agent:** Mistral-7B (via OpenAI client) with HuggingFace Zephyr-7b-beta judge

**Actual Test Run (April 10, 2026):**

| Task | Score | Notes |
|------|-------|-------|
| Easy | 0.500 | Caught 4/8 structured PIIs (Aadhaar, PAN, email detected; phone missed) |
| Medium | 0.440 | NER + HF validation working; partial context understanding |
| Hard | 0.230 | 3 attempts, all scored 0.230 (re-identification risk remains high) |
| **Overall** | **0.390** | Low baseline shows room for agent improvement (feature, not bug) |

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

