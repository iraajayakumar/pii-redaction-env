# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.


"""Pii Redaction Env Environment Client."""


from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

try:
    from .models import PiiRedactionAction, PiiRedactionObservation
except ImportError:
    from models import PiiRedactionAction, PiiRedactionObservation


class PiiRedactionEnv(
    EnvClient[PiiRedactionAction, PiiRedactionObservation, State]
):
    """
    Client for the PII Redaction Environment.
    
    Connects to the PII redaction server and handles reset/step/state operations.
    """

    def _step_payload(self, action: PiiRedactionAction) -> Dict:
        """Convert PiiRedactionAction to JSON payload for step message."""
        return action.model_dump(mode="json")

    def _parse_result(self, payload: Dict) -> StepResult[PiiRedactionObservation]:
        """Parse server response into StepResult[PiiRedactionObservation]."""
        obs_data = payload.get("observation", {})
        observation = PiiRedactionObservation.model_validate(obs_data)
        
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """Parse server response into State object."""
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )