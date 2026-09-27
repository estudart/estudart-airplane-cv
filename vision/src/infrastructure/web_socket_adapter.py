import asyncio
import json

from websockets.asyncio.client import ClientConnection, connect


class WebSocketAdapter:
    def __init__(self, uri: str):
        self._uri = uri
        self._wss: ClientConnection | None = None

    async def connect(self):
        retries = 0
        while retries < 3:
            try:
                self._wss = await connect(self._uri)
                print("Connection established with the server!")
                return
            except Exception as err:
                print(f"Could not establish connection, reason: {err}")
                retries += 1
                await asyncio.sleep(10)

        raise RuntimeError(f"Could not connect to WebSocket server: {self._uri}")

    async def send_message(self, msg_type: str, message: str) -> None:
        if not self._wss:
            raise RuntimeError("WebSocket is not connected!")

        await self._wss.send(json.dumps({
            "type": msg_type,
            "message": message,
        }))

