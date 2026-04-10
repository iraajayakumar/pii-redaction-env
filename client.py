# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Pii Redaction Env Environment Client."""

import os
from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import PiiRedactionAction, PiiRedactionObservation


class PiiRedactionEnv(
    EnvClient[PiiRedactionAction, PiiRedactionObservation, State]
):
    """
    Client for the Pii Redaction Env Environment.

    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions with lower latency.
    Each client instance has its own dedicated environment session on the server.

    Supports multiple task types (easy, medium, hard) via task_type parameter.

    Example:
        >>> # Connect to a running server and run easy task
        >>> client = PiiRedactionEnv(base_url="http://localhost:8000", task_type="easy")
        >>> result = client.reset()
        >>> result = client.step(PiiRedactionAction(redacted_text="redacted text"))

    Example with Docker:
        >>> client = PiiRedactionEnv.from_docker_image("pii_redaction_env-env:latest", task_type="medium")
        >>> result = client.reset()
        >>> result = client.step(PiiRedactionAction(redacted_text="redacted text"))
    """

    def __init__(self, base_url: str = "http://localhost:8000", task_type: str = "easy", **kwargs):
        """
        Initialize the PiiRedactionEnv client.
        
        Args:
            base_url: Server URL (default: http://localhost:8000)
            task_type: Task type - one of "easy", "medium", "hard" (default: "easy")
            **kwargs: Additional arguments passed to EnvClient
        """
        # CRITICAL: Set environment variable for server-side task type detection
        # This ensures that when the server's environment is created, it knows which task to use
        os.environ["TASK_TYPE"] = task_type
        
        super().__init__(base_url=base_url, **kwargs)
        self.task_type = task_type
        self._base_url = base_url
        
        # Ensure task_type is configured on server immediately
        # This works even if client and server are in separate processes
        self._configure_task_on_server()

    def _configure_task_on_server(self) -> None:
        """
        Configure task_type on the server before any reset() calls.
        
        This ensures the server knows which task to use when creating the environment,
        even if client and server are in separate processes (e.g., Docker).
        """
        try:
            import requests
            # Make explicit HTTP call to configure server
            configure_url = f"{self._base_url.rstrip('/')}/configure_task"
            response = requests.post(
                configure_url,
                params={"task_type": self.task_type},
                timeout=5
            )
            if response.status_code not in (200, 201):
                # Configuration endpoint might not exist on older servers
                # This is OK - fall back to environment variable
                print(f"[DEBUG] Config endpoint returned {response.status_code}, using env var fallback", flush=True)
        except Exception as e:
            # Configuration endpoint doesn't exist or server is not reachable yet
            # The environment variable fallback will be used instead
            print(f"[DEBUG] Failed to configure task_type on server: {e}", flush=True)

    def _step_payload(self, action: PiiRedactionAction) -> Dict:
        """
        Convert PiiRedactionAction to JSON payload for step message.

        Args:
            action: PiiRedactionAction instance with redacted_text

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "redacted_text": action.redacted_text,
            "identified_pii_types": action.identified_pii_types,
            "reasoning": action.reasoning,
        }

    def _parse_result(self, payload: Dict) -> StepResult[PiiRedactionObservation]:
        """
        Parse server response into StepResult[PiiRedactionObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with PiiRedactionObservation
        """
        obs_data = payload.get("observation", {})
        observation = PiiRedactionObservation(
            document_text=obs_data.get("document_text", ""),
            task_type=obs_data.get("task_type", self.task_type),
            instructions=obs_data.get("instructions", ""),
            legal_framework=obs_data.get("legal_framework", "DPDP Act 2023"),
            attempt_number=obs_data.get("attempt_number", 1),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """
        Parse server response into State object.

        Args:
            payload: JSON response from state request

        Returns:
            State object with episode_id and step_count
        """
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
