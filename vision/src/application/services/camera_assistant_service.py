from src.application.errors.unknown_agent_error import UnknownAgentError
from src.application.ports.camera_agent_port import CameraAgentPort


class CameraAssistant:
    def __init__(self, camera_agent: CameraAgentPort) -> None:
        self._agent_map: dict[str, CameraAgentPort] = {
            "camera-agent": camera_agent,
        }

    async def invoke(self, agent: str, question: str) -> str:
        if agent not in self._agent_map:
            raise UnknownAgentError(f"Agent {agent} does not exist!")

        return await self._agent_map[agent].invoke_agent(question)
