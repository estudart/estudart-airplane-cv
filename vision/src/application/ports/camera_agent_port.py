from typing import Protocol


class CameraAgentPort(Protocol):
    async def invoke_agent(self, question: str) -> str:
        ...
