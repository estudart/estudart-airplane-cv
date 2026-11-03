import json
import logging
from types import SimpleNamespace

from src.application.agents.camera_agent import CameraAgent
from src.application.services.logging_service import LoggerService

CAPTURE_IMAGE_TOOL = {
    "name": "capture_image",
    "description": "Return the latest frame.",
    "input_schema": {"type": "object", "properties": {}},
}


def tool_call(name: str, arguments: dict) -> SimpleNamespace:
    return SimpleNamespace(
        id=f"call-{name}",
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


def completion(content: str | None, tool_calls: list | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(
            message=SimpleNamespace(content=content, tool_calls=tool_calls),
        )],
    )


class FakeLLMClient:
    def __init__(self, completions: list):
        self._completions = completions
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    async def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self._completions.pop(0)


class FakeMCPAdapter:
    def __init__(self, blocks: list[dict] | None = None, error: Exception | None = None):
        self._blocks = blocks or []
        self._error = error
        self.called = []

    async def list_tools(self):
        return [CAPTURE_IMAGE_TOOL]

    async def call_tool(self, tool_name: str, arguments: dict):
        self.called.append((tool_name, arguments))
        if self._error:
            raise self._error
        return self._blocks


def build_agent(llm_client: FakeLLMClient, mcp_adapter: FakeMCPAdapter) -> CameraAgent:
    return CameraAgent(
        system_prompt="You watch a camera.",
        model="gpt-4o-mini",
        llm_client_factory=lambda: llm_client,
        mcp_adapter=mcp_adapter,
        mcp_tools=[CAPTURE_IMAGE_TOOL],
        logger_service=LoggerService(level=logging.INFO),
    )


async def test_answers_without_calling_a_tool():
    llm_client = FakeLLMClient([completion("Hello there!")])
    mcp_adapter = FakeMCPAdapter()

    answer = await build_agent(llm_client, mcp_adapter).invoke_agent("Hi")

    assert answer == "Hello there!"
    assert mcp_adapter.called == []
    assert llm_client.calls[0]["tools"][0]["function"]["name"] == "capture_image"


async def test_replays_a_captured_frame_as_an_image_message():
    llm_client = FakeLLMClient([
        completion(None, [tool_call("capture_image", {})]),
        completion("I see an airplane."),
    ])
    mcp_adapter = FakeMCPAdapter(
        blocks=[{"type": "image", "data": "ZmFrZQ==", "mime_type": "image/jpeg"}]
    )

    answer = await build_agent(llm_client, mcp_adapter).invoke_agent("What do you see?")

    assert answer == "I see an airplane."
    assert mcp_adapter.called == [("capture_image", {})]

    messages = llm_client.calls[-1]["messages"]
    image_message = messages[-1]
    assert image_message["role"] == "user"
    assert image_message["content"][1]["image_url"]["url"] == (
        "data:image/jpeg;base64,ZmFrZQ=="
    )
    assert messages[-2]["role"] == "tool"
    assert messages[-2]["tool_call_id"] == "call-capture_image"


async def test_feeds_a_failed_tool_back_to_the_model():
    llm_client = FakeLLMClient([
        completion(None, [tool_call("capture_image", {})]),
        completion("No frame is available yet."),
    ])
    mcp_adapter = FakeMCPAdapter(error=RuntimeError("No camera frame is available yet"))

    answer = await build_agent(llm_client, mcp_adapter).invoke_agent("What do you see?")

    assert answer == "No frame is available yet."
    tool_message = llm_client.calls[-1]["messages"][-1]
    assert tool_message["role"] == "tool"
    assert "No camera frame is available yet" in tool_message["content"]
