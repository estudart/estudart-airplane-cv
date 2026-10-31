import json
from typing import Any, Callable

from src.application.ports.mcp_port import MCPPort
from src.application.services.logging_service import LoggerService


class CameraAgent:
    def __init__(
        self,
        system_prompt: str,
        model: str,
        llm_client_factory: Callable[[], Any],
        mcp_adapter: MCPPort,
        mcp_tools: list[dict[str, Any]],
        logger_service: LoggerService,
        max_tool_turns: int = 5,
    ) -> None:
        self._system_prompt = system_prompt
        self._model = model
        self._llm_client_factory = llm_client_factory
        self._llm_client: Any | None = None
        self._mcp_adapter = mcp_adapter
        self._mcp_tools = mcp_tools
        self._logger_service = logger_service
        self._max_tool_turns = max_tool_turns

    def _llm(self) -> Any:
        """Build the chat client on first use, so a missing API key only breaks
        the chat and never the camera stream sharing this socket."""
        if not self._llm_client:
            self._llm_client = self._llm_client_factory()
        return self._llm_client

    def _tool_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
            for tool in self._mcp_tools
        ]

    def _tool_messages(
        self,
        tool_call_id: str,
        blocks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Turn MCP content blocks into messages the chat model understands.

        A tool message only carries text, so an image block is replayed as an
        extra user message holding the frame as a data URL.
        """
        texts = [block["text"] for block in blocks if block["type"] == "text"]
        images = [block for block in blocks if block["type"] == "image"]

        messages: list[dict[str, Any]] = [{
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": "\n".join(texts) if texts else "See the attached camera frame.",
        }]

        for image in images:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Latest camera frame."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image['mime_type']};base64,{image['data']}"
                        },
                    },
                ],
            })

        return messages

    async def _run_tool_call(self, tool_call: Any) -> list[dict[str, Any]]:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments or "{}")

        try:
            blocks = await self._mcp_adapter.call_tool(tool_name, arguments)
        except Exception as err:
            self._logger_service.log_error_message(
                f"Tool {tool_name} failed, reason: {err}"
            )
            blocks = [{"type": "text", "text": f"Tool {tool_name} failed: {err}"}]

        return self._tool_messages(tool_call.id, blocks)

    async def invoke_agent(self, question: str) -> str:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": question},
        ]

        for _ in range(self._max_tool_turns):
            completion = await self._llm().chat.completions.create(
                model=self._model,
                messages=messages,
                tools=self._tool_schemas(),
            )
            answer = completion.choices[0].message

            if not answer.tool_calls:
                return answer.content or ""

            messages.append({
                "role": "assistant",
                "content": answer.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in answer.tool_calls
                ],
            })

            for tool_call in answer.tool_calls:
                messages.extend(await self._run_tool_call(tool_call))

        raise RuntimeError(
            f"CameraAgent did not answer within {self._max_tool_turns} tool turns"
        )
