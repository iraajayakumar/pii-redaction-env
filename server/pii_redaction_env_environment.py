# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

from __future__ import annotations

import os
from uuid import uuid4
from typing import Dict, Any, ClassVar, List

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
    OpenEnv-compatible PII redaction environment.

    Supports 3 task families:
    - easy
    - medium
    - hard

    Validation-friendly behavior:
    - If task_type is explicitly provided (constructor or env var), use it.
    - If not provided, cycle across easy -> medium -> hard for successive episodes.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    AVAILABLE_TASKS: ClassVar[List[str]] = ["easy", "medium", "hard"]
    _cycle_index: ClassVar[int] = 0

    def __init__(self, task_type: str | None = None):
        explicit_task = task_type or os.getenv("TASK_TYPE")
        if explicit_task is not None and explicit_task not in self.AVAILABLE_TASKS:
            raise ValueError(
                f"Unknown task_type '{explicit_task}'. "
                f"Must be one of: {self.AVAILABLE_TASKS}"
            )

        self.task_type = explicit_task
        self._selected_task_type: str | None = None
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task: Dict[str, Any] = {}
        self._done: bool = False

    @classmethod
    def _next_task_type(cls) -> str:
        task = cls.AVAILABLE_TASKS[cls._cycle_index % len(cls.AVAILABLE_TASKS)]
        cls._cycle_index += 1
        return task

    def _resolve_task_type(self) -> str:
        if self.task_type in self.AVAILABLE_TASKS:
            return self.task_type
        return self._next_task_type()

    def _load_task(self, task_type: str) -> Dict[str, Any]:
        if task_type == "easy":
            return get_easy_task()
        if task_type == "medium":
            return get_medium_task()
        if task_type == "hard":
            return get_hard_task()
        raise ValueError(f"Unknown task_type '{task_type}'")

    def reset(self) -> PIIObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._done = False

        self._selected_task_type = self._resolve_task_type()
        self._current_task = self._load_task(self._selected_task_type)

        return PIIObservation(
            document_text=self._current_task["document_text"],
            task_type=self._current_task["task_type"],
            instructions=self._current_task["instructions"],
            legal_framework=self._current_task.get("legal_framework", "DPDP Act 2023"),
            attempt_number=1,
        )

    def step(self, action: PIIAction):  # type: ignore[override]
        self._state.step_count += 1

        if self._done:
            return (
                PIIObservation(
                    document_text="Episode complete. Call reset() to start a new episode.",
                    task_type=self._selected_task_type or self.task_type or "unknown",
                    instructions="",
                    legal_framework="DPDP Act 2023",
                    attempt_number=self._state.step_count,
                ),
                0.0,
                True,
                {"error": "Step called after episode ended. Call reset() first."},
            )

        active_task = self._selected_task_type or self.task_type or "easy"

        if active_task == "easy":
            result = grade_easy_task(
                original_text=self._current_task["document_text"],
                redacted_text=action.redacted_text,
                pii_present=self._current_task["pii_present"],
            )
            self._done = True

        elif active_task == "medium":
            result = grade_medium_task(
                original_text=self._current_task["document_text"],
                redacted_text=action.redacted_text,
                pii_present=self._current_task["pii_present"],
            )
            self._done = True

        elif active_task == "hard":
            result = grade_hard_task(
                original_text=self._current_task["document_text"],
                redacted_text=action.redacted_text,
                pii_present=self._current_task["pii_present"],
                attempt_number=self._state.step_count,
            )
            self._done = result.get("episode_done", True)

        else:
            raise ValueError(f"Unknown task_type: {active_task}")

        next_observation = PIIObservation(
            document_text=action.redacted_text,
            task_type=active_task,
            instructions=result.get("feedback", ""),
            legal_framework="DPDP Act 2023",
            attempt_number=self._state.step_count,
        )

        reward = float(result.get("score", 0.0))
        return next_observation, reward, self._done, result

    def state(self) -> State:
        return self._state