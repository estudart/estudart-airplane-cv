from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.application.errors.unknown_agent_error import UnknownAgentError
from src.dependencies import get_camera_assistant

camera_agent_router = APIRouter(prefix="/api", tags=["camera agent"])


class AgentQuestion(BaseModel):
    question: str
    agent: str = "camera-agent"


class AgentAnswer(BaseModel):
    agent: str
    message: str


@camera_agent_router.post("/camera-assistant", response_model=AgentAnswer)
async def ask_camera_assistant(payload: AgentQuestion) -> AgentAnswer:
    """Ask the camera agent over plain REST.

    The browser chat uses the WebSocket instead, because it needs the answer on
    the same connection that already carries the camera frames. This route is
    the request/response door to the same agent.
    """
    camera_assistant = await get_camera_assistant()

    try:
        answer = await camera_assistant.invoke(payload.agent, payload.question)
    except UnknownAgentError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    return AgentAnswer(agent=payload.agent, message=answer)
