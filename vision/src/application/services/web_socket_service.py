import json

from src.application.services.camera_assistant_service import CameraAssistant
from src.application.services.logging_service import LoggerService
from src.application.ports.web_socket_connection_port import WebSocketConnectionPort

CAMERA_FRAME_TYPE = "camera-frame"


class WebSocketService:
    """Routes the single camera socket: frames fan out, questions reach an agent.

    A producer (the camera streamer) pushes `camera-frame` messages. A consumer
    that subscribed with `?subscribeType=camera-data-consumer&detected=true`
    receives every frame. Any other message type is an agent name, and the
    answer goes back only to the connection that asked.
    """

    def __init__(
        self,
        camera_assistant: CameraAssistant,
        logger_service: LoggerService,
    ) -> None:
        self._camera_assistant = camera_assistant
        self._logger_service = logger_service
        self._connections: list[WebSocketConnectionPort] = []

    def subscribe(
        self,
        connection: WebSocketConnectionPort,
        query_params: dict[str, str],
    ) -> None:
        if (
            query_params.get("subscribeType") == "camera-data-consumer"
            and query_params.get("detected") == "true"
        ):
            self._connections.append(connection)
            self._logger_service.log_info_message("New camera frame consumer connected")

    def unsubscribe(self, connection: WebSocketConnectionPort) -> None:
        self._connections = [
            subscriber for subscriber in self._connections if subscriber is not connection
        ]
        self._logger_service.log_info_message("Connection closed")

    async def broadcast_frame(self, frame: str) -> None:
        for connection in list(self._connections):
            try:
                await connection.send_text(
                    json.dumps({"type": CAMERA_FRAME_TYPE, "frame": frame})
                )
            except Exception as err:
                self._logger_service.log_error_message(
                    f"Could not send frame to a consumer, reason: {err}"
                )
                self.unsubscribe(connection)

    async def handle_message(
        self,
        connection: WebSocketConnectionPort,
        raw_message: str,
    ) -> None:
        try:
            data = json.loads(raw_message)
            message_type = data.get("type")

            if message_type == CAMERA_FRAME_TYPE:
                await self.broadcast_frame(data.get("message", ""))
                return

            agent = message_type
            answer = await self._camera_assistant.invoke(agent, data.get("question", ""))

            await connection.send_text(
                json.dumps({"type": "response", "message": answer, "agent": agent})
            )
        except Exception as err:
            self._logger_service.log_error_message(
                f"Could not handle socket message, reason: {err}"
            )
            await connection.send_text(json.dumps({"type": "error", "message": str(err)}))
