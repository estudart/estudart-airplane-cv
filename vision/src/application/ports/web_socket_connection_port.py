from typing import Protocol


class WebSocketConnectionPort(Protocol):
    async def send_text(self, data: str) -> None:
        ...
