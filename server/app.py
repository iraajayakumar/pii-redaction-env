# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the Pii Redaction Env Environment.

This module creates an HTTP server that exposes the PiiRedactionEnvironment
over HTTP and WebSocket endpoints, compatible with EnvClient.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - WS /ws: WebSocket endpoint for persistent sessions

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

    # Or run directly:
    python -m server.app
"""

import os
import threading
from contextvars import ContextVar
from typing import Dict, Any

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

try:
    from ..models import PIIAction, PIIObservation
    from .pii_redaction_env_environment import PIIRedactionEnvironment
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models import PIIAction, PIIObservation
    from server.pii_redaction_env_environment import PIIRedactionEnvironment

# Context variable for storing task_type per async context/request
# This handles the case where client and server are in separate processes
_task_type_context: ContextVar[str] = ContextVar('task_type', default='easy')

# Thread-local storage for task_type (for sync contexts)
_thread_local = threading.local()

# Global task type tracking (fallback for concurrent environments)
# Maps environment ID to task type
_env_task_types: Dict[str, str] = {}


def set_context_task_type(task_type: str) -> None:
    """
    Set the task_type for the current context.
    Used when client and server are in the same process.
    """
    if task_type in ['easy', 'medium', 'hard']:
        _task_type_context.set(task_type)
        _thread_local.task_type = task_type
        # Also set environment variable for subprocesses
        os.environ["TASK_TYPE"] = task_type


def get_context_task_type() -> str:
    """Get the task_type from the current context."""
    # Try context var first (async)
    try:
        return _task_type_context.get()
    except LookupError:
        pass
    
    # Try thread local next
    if hasattr(_thread_local, 'task_type'):
        return _thread_local.task_type
    
    # Finally try environment variable
    return os.getenv("TASK_TYPE", "easy")


def pii_env_factory(**kwargs) -> PIIRedactionEnvironment:
    """
    Factory function to create PIIRedactionEnvironment with task_type support.
    
    This factory attempts to determine task_type from multiple sources:
    1. Context variable (set by request handler)
    2. Thread-local storage
    3. Environment variable (set by client)
    4. Request metadata/headers
    5. Default to "easy"
    """
    task_type = get_context_task_type()
    env_id = kwargs.get("env_id")
    
    # Store mapping for future reference
    if env_id:
        _env_task_types[env_id] = task_type
    
    print(f"[DEBUG] Factory creating environment with task_type='{task_type}'", flush=True)
    return PIIRedactionEnvironment(task_type=task_type)


# Create the app with the improved factory
app = create_app(
    pii_env_factory,
    PIIAction,
    PIIObservation,
    env_name="pii_redaction_env",
    max_concurrent_envs=1,  # increase this number to allow more concurrent WebSocket sessions
)


# Optional: Add a configuration endpoint that the client can call
# This provides an explicit way to set task_type before reset()
@app.post("/configure_task")
async def configure_task(task_type: str) -> Dict[str, Any]:
    """
    Configure task type for the next environment reset.
    
    This endpoint allows explicit task_type configuration when
    client and server are in separate processes.
    
    Args:
        task_type: One of "easy", "medium", "hard"
    
    Returns:
        Status response
    """
    if task_type not in ['easy', 'medium', 'hard']:
        return {"status": "error", "message": f"Invalid task_type: {task_type}"}
    
    set_context_task_type(task_type)
    print(f"[DEBUG] Task type configured to '{task_type}'", flush=True)
    return {"status": "ok", "task_type": task_type}


# Health check and root endpoints for deployment (HF Space, Docker, etc.)
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint - health check and API info."""
    return {
        "status": "running",
        "service": "pii_redaction_env",
        "version": "1.0",
        "description": "PII Redaction Environment - OpenEnv compatible server"
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for deployment systems (Kubernetes, HF Space, etc.)."""
    return {"status": "healthy", "service": "pii_redaction_env"}


def main(host: str = "0.0.0.0", port: int = 8000):
    """
    Entry point for direct execution via uv run or python -m.

    This function enables running the server without Docker:
        uv run --project . server
        uv run --project . server --port 8001
        python -m pii_redaction_env.server.app

    Args:
        host: Host address to bind to (default: "0.0.0.0")
        port: Port number to listen on (default: 8000)

    For production deployments, consider using uvicorn directly with
    multiple workers:
        uvicorn pii_redaction_env.server.app:app --workers 4
    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
