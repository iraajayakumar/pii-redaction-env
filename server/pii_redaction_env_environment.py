# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Pii Redaction Env Environment Implementation.
Implements the OpenEnv interface: reset(), step(), state().
Supports three task types: easy, medium, hard.
"""

from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import PIIAction, PIIObservation
except ImportError:
    from models import PIIAction, PIIObservation
    
from server.tasks.easy import get_easy_task
from server.tasks.medium import get_medium_task
from server.tasks.hard import get_hard_task
from server.graders.easy_grader import grade_easy_task
from server.graders.medium_grader import grade_medium_task
from server.graders.hard_grader import grade_hard_task


class PIIRedactionEnvironment(Environment):
    """
    OpenEnv-compatible environment for PII redaction tasks.
    
    The environment simulates the workflow of a Data Privacy Officer
    processing sensitive Indian documents under the DPDP Act 2023.
    
    Task flow:
    1. reset() — loads a document, returns it as an observation
    2. step(action) — receives the agent's redacted document, grades it,
                      returns next observation + reward + done flag
    3. state() — returns current episode state for logging
    
    The environment is single-step for easy and medium tasks:
    the agent gets one attempt, receives a score, and the episode ends.
    
    For hard tasks, the environment is multi-step:
    attempt 1 — agent redacts
    attempt 2 — environment reveals re-identification result,
                agent must redact more aggressively
    """

    # Enable concurrent WebSocket sessions.
    # Set to True if your environment isolates state between instances.
    # When True, multiple WebSocket clients can connect simultaneously, each
    # getting their own environment instance (when using factory mode in app.py).
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self, task_type: str = "easy"):
        """
        Initialize the pii_redaction_env environment.
        Args:
            task_type: One of "easy", "medium", "hard".
                       Defaults to "easy" so the environment works
                       out of the box without configuration.
        """
        self.task_type = task_type
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task: dict = {}
        self._done: bool = False

    def reset(self) -> PIIObservation:
        """
        Reset the environment.
        Starts a new episode. Loads a fresh document and returns it.
        Called by the agent/trainer at the start of each episode.
        
        Returns:
            PIIObservation containing the document and instructions.
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._done = False
        
        if self.task_type == "easy":
            self._current_task = get_easy_task()
        elif self.task_type == "medium":
            self._current_task = get_medium_task()
        elif self.task_type == "hard":
            self._current_task = get_hard_task()
        else:
            raise ValueError(
                f"Unknown task_type '{self.task_type}'. "
                f"Must be one of: 'easy', 'medium', 'hard'."
            )

        return PIIObservation(
            document_text=self._current_task["document_text"],
            task_type=self._current_task["task_type"],
            instructions=self._current_task["instructions"],
            legal_framework=self._current_task["legal_framework"],
            attempt_number=1,
        )

    def step(self, action: PIIAction) -> PIIObservation:  # type: ignore[override]
        """
        Processes the agent's action (redacted document) and returns a result.
        
        Args:
            action: PIIAction containing the agent's redacted_text,
                    identified_pii_types, and reasoning.
        
        Returns:
            Tuple of (next_observation, reward, done, info)
            - next_observation: PIIObservation with feedback
            - reward: float between 0.0 and 1.0
            - done: bool — True means episode is over
            - info: dict with detailed grading results
        """
        self._state.step_count += 1
        
        if self._done:
            # Agent called step() after the episode ended.
            # Return a terminal observation with zero reward.
            return (
                PIIObservation(
                    document_text="Episode complete. Call reset() to start a new episode.",
                    task_type=self.task_type,
                    instructions="",
                    legal_framework="DPDP Act 2023",
                    attempt_number=self._state.step_count,
                ),
                0.0,    # reward = 0 for post-episode steps
                True,   # done = True, episode still over
                {"error": "Step called after episode ended. Call reset() first."}
            )
            
        # --- Grade the action based on task type ---
        if self.task_type == "easy":
            result = grade_easy_task(
                original_text=self._current_task["document_text"],
                redacted_text=action.redacted_text,
                pii_present=self._current_task["pii_present"],
            )
            self._done = True
            # Easy task is single-step — one attempt, episode over.

        elif self.task_type == "medium":
            result = grade_medium_task(
                original_text=self._current_task["document_text"],
                redacted_text=action.redacted_text,
                pii_present=self._current_task["pii_present"],
            )
            self._done = True
            # Medium task is also single-step.

        elif self.task_type == "hard":
            result = grade_hard_task(
                original_text=self._current_task["document_text"],
                redacted_text=action.redacted_text,
                pii_present=self._current_task["pii_present"],
                attempt_number=self._state.step_count,
            )
            # Hard task uses step_count to know which attempt this is.
            # The grader decides whether to end the episode.
            self._done = result.get("episode_done", True)
            # result["episode_done"] lets the hard grader control
            # whether to give the agent another attempt.
            # Default True means single-step unless grader says otherwise.

        else:
            raise ValueError(f"Unknown task_type: {self.task_type}")
        
        # --- Build next observation with feedback ---
        next_observation = PIIObservation(
            document_text=action.redacted_text,
            # After grading, the "document" the agent sees is its own submission.
            # In the hard task, this lets the agent see what it submitted
            # and revise it in the next step.

            task_type=self.task_type,
            instructions=result["feedback"],
            # The feedback from the grader becomes the new instructions.
            # This gives the agent rich signal about what it got right/wrong.

            legal_framework="DPDP Act 2023",
            attempt_number=self._state.step_count,
        )

        reward = result["score"]
        # The score from the grader IS the reward.
        # 0.0 = failed completely, 1.0 = perfect redaction.

        return next_observation, reward, self._done, result
        # OpenEnv step() must return exactly this 4-tuple.
        # (observation, reward, done, info)
        # result dict is the info — detailed grading breakdown for logging.

    def state(self) -> State:
        """
        Returns current episode state.
        Called by OpenEnv to track episode progress for logging.
        
        Returns:
            State object with episode_id and step_count.
        """
        return self._state
        # Simple — just return the state object we've been maintaining.
        # OpenEnv uses this for telemetry and the web UI.
