import json
import logging

from src.application.services.camera_assistant_service import CameraAssistant
from src.application.services.logging_service import LoggerService
from src.application.services.web_socket_service import WebSocketService


class FakeConnection:
    def __init__(self):
        self.sent = []

    async def send_text(self, data: str) -> None:
        self.sent.append(json.loads(data))


class FakeCameraAgent:
    async def invoke_agent(self, question: str) -> str:
        return f"CameraAgent: {question}"


def build_service() -> WebSocketService:
    return WebSocketService(
        camera_assistant=CameraAssistant(camera_agent=FakeCameraAgent()),
        logger_service=LoggerService(level=logging.INFO),
    )


CONSUMER_PARAMS = {"subscribeType": "camera-data-consumer", "detected": "true"}


async def test_streams_camera_frames_to_detected_consumers():
    service = build_service()
    consumer = FakeConnection()
    producer = FakeConnection()

    service.subscribe(consumer, CONSUMER_PARAMS)
    service.subscribe(producer, {})

    await service.handle_message(
        producer,
        json.dumps({"type": "camera-frame", "message": "frame-b64"}),
    )

    assert consumer.sent == [{"type": "camera-frame", "frame": "frame-b64"}]
    assert producer.sent == []


async def test_answers_camera_agent_messages():
    service = build_service()
    chat = FakeConnection()
    service.subscribe(chat, {})

    await service.handle_message(
        chat,
        json.dumps({"type": "camera-agent", "question": "What do you see?"}),
    )

    assert chat.sent == [{
        "type": "response",
        "message": "CameraAgent: What do you see?",
        "agent": "camera-agent",
    }]


async def test_does_not_subscribe_consumers_without_detected_true():
    service = build_service()
    consumer = FakeConnection()

    service.subscribe(consumer, {"subscribeType": "camera-data-consumer"})

    assert consumer not in service._connections


async def test_reports_unknown_agent_as_socket_error():
    service = build_service()
    chat = FakeConnection()

    await service.handle_message(
        chat,
        json.dumps({"type": "ghost-agent", "question": "Are you there?"}),
    )

    assert chat.sent[0]["type"] == "error"
    assert "ghost-agent" in chat.sent[0]["message"]


async def test_drops_a_consumer_that_fails_to_receive():
    service = build_service()

    class BrokenConnection(FakeConnection):
        async def send_text(self, data: str) -> None:
            raise ConnectionError("socket is gone")

    broken = BrokenConnection()
    service.subscribe(broken, CONSUMER_PARAMS)

    await service.broadcast_frame("frame-b64")

    assert service._connections == []


async def test_unsubscribe_removes_only_the_closed_connection():
    service = build_service()
    first, second = FakeConnection(), FakeConnection()
    service.subscribe(first, CONSUMER_PARAMS)
    service.subscribe(second, CONSUMER_PARAMS)

    service.unsubscribe(first)

    assert service._connections == [second]
