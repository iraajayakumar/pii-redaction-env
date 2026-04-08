# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Pii Redaction Env Environment.

The pii_redaction_env environment is a realistic testbed designed to evaluate and train AI agents for automated PII (Personally Identifiable Information) and PHI (Protected Health Information) detection, classification, and redaction. It simulates real-world compliance scenarios by providing progressively challenging tasks, from detecting direct identifiers to handling contextual, indirect PII, and resisting de-anonymization attacks..
"""

from openenv.core.env_server.types import Action, Observation
from pydantic import Field
from typing import Optional, List, Dict

class PIIAction(Action):
    """Action for the Pii Redaction Env environment - a redacted version of the document."""
    redacted_text: str = Field(
        ...,
        description="The document text with PII replaced by [REDACTED] tags"
    )
    identified_pii_types: List[str] = Field(
        default_factory=list,
        description="List of PII types the agent identified e.g. ['AADHAAR', 'PAN', 'PHONE']"
    )
    reasoning: str = Field(
        default="",
        description="Agent's explanation of what it redacted and why"
    )

class PIIObservation(Observation):
    """What the agent sees — the document and task instructions."""
    document_text: str = Field(
        ...,
        description="The raw document text containing PII to be redacted"
    )
    task_type: str = Field(
        ...,
        description="One of: easy, medium, hard"
    )
    instructions: str = Field(
        ...,
        description="Specific instructions for this task"
    )
    legal_framework: str = Field(
        default="DPDP Act 2023",
        description="The legal framework to comply with"
    )
    attempt_number: int = Field(
        default=1,
        description="Which attempt this is (relevant for hard task)"
    )
    
class PIIReward(Action):
    """Reward model — not used directly but defines reward structure."""
    score: float = Field(..., description="Score between 0.0 and 1.0")
    feedback: str = Field(..., description="Explanation of the score")


# Backward compatibility aliases
PiiRedactionAction = PIIAction
PiiRedactionObservation = PIIObservation
