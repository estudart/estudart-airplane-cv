from typing import Any, Protocol


class MCPPort(Protocol):
    async def list_tools(self) -> list[dict[str, Any]]:
        ...

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> list[dict[str, Any]]:
        ...
