from typing import Any

from fastmcp import Client, FastMCP


class MCPAdapter:
    """Talks to the camera tools through the MCP protocol, in this process.

    The tools stay behind the MCP boundary even though the server object lives
    in the same FastAPI app, so the agent sees exactly what a remote MCP client
    would see.
    """

    def __init__(self, mcp_server: FastMCP) -> None:
        self._mcp_server = mcp_server

    async def list_tools(self) -> list[dict[str, Any]]:
        async with Client(self._mcp_server) as client:
            tools = await client.list_tools()

        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.input_schema,
            }
            for tool in tools
        ]

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> list[dict[str, Any]]:
        async with Client(self._mcp_server) as client:
            result = await client.call_tool(tool_name, arguments)

        return [self._content_block(block) for block in result.content]

    def _content_block(self, block: Any) -> dict[str, Any]:
        if block.type == "image":
            return {
                "type": "image",
                "data": block.data,
                "mime_type": block.mime_type,
            }

        if block.type == "text":
            return {"type": "text", "text": block.text}

        return {"type": "text", "text": block.model_dump_json()}
