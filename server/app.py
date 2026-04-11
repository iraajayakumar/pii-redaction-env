# server/app.py - FULL REPLACEMENT
"""
Custom FastAPI app with task parameter forwarding for PII Redaction Env.
"""

from fastapi import FastAPI, Body, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from typing import Optional, Dict, Any
from pydantic import BaseModel

try:
    from ..models import PIIAction, PIIObservation
    from .pii_redaction_env_environment import PIIRedactionEnvironment
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models import PIIAction, PIIObservation
    from server.pii_redaction_env_environment import PIIRedactionEnvironment

app = FastAPI(title="PII Redaction Environment")

# Single global environment instance (max_concurrent_envs=1)
env = PIIRedactionEnvironment(task_type=None)  # Will use cycling/default

class ResetRequest(BaseModel):
    task: Optional[str] = None

class StepRequest(BaseModel):
    action: dict

@app.post("/reset")
async def reset_endpoint(
    body: Optional[ResetRequest] = Body(default=None),
    task: Optional[str] = Query(default=None),
):
    selected_task = task or (body.task if body else None)
    obs = env.reset(task=selected_task)
    return {
        "observation": obs.model_dump(),
        "reward": None,
        "done": False
    }

@app.post("/step")
async def step_endpoint(request: StepRequest = Body(...)):
    """Execute action with flexible field mapping."""
    action_dict = request.action.copy()
    
    # Handle both field name variants for maximum compatibility
    field_mapping = {
        "redacted_document": "redacted_text",
        "redacted_text": "redacted_text"
    }
    
    # Remap fields if needed
    for old_name, new_name in field_mapping.items():
        if old_name in action_dict and old_name != new_name:
            action_dict[new_name] = action_dict.pop(old_name)
    
    action = PIIAction(**action_dict)
    obs, reward, done = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done
    }

@app.get("/state")
async def state_endpoint():
    """Get current environment state."""
    state = env.state
    return {
        "episode_id": state.episode_id,
        "step_count": state.step_count
    }

@app.get("/schema")
async def schema_endpoint():
    """Return action/observation schemas."""
    return {
        "action_schema": PIIAction.model_json_schema(),
        "observation_schema": PIIObservation.model_json_schema()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for persistent sessions."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("method") == "reset":
                task = data.get("params", {}).get("task")
                obs = env.reset(task=task)
                await websocket.send_json({
                    "observation": obs.model_dump(),
                    "reward": None,
                    "done": False
                })
            elif data.get("method") == "step":
                action_dict = data["params"]["action"]
                action = PIIAction(**action_dict)
                obs = env.step(action)
                await websocket.send_json({
                    "observation": obs.model_dump(),
                    "reward": obs.reward,
                    "done": obs.done
                })
            elif data.get("method") == "state":
                state = env.state
                await websocket.send_json({
                    "episode_id": state.episode_id,
                    "step_count": state.step_count
                })
    except WebSocketDisconnect:
        pass
    
@app.get("/health")
async def health_check():
    """Health check endpoint required by validator."""
    return {"status": "healthy", "environment": "pii_redaction_env"}

def main(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()