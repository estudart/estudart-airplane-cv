from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.utilities.types import Image

from src.config import settings
from src.dependencies import get_logger_service, get_redis_adapter


mcp = FastMCP("Camera Tools")


async def _capture_latest_frame() -> bytes:
    redis_adapter = get_redis_adapter()
    frame = await redis_adapter.get_key(settings.CAMERA_FRAME_KEY)
    if frame is None:
        raise RuntimeError("No camera frame is available yet")
    return frame


@mcp.tool(tags={"capture-image"})
async def capture_image() -> Image:
    """Return the latest detected JPEG frame stored by the camera streamer."""
    try:
        frame = await _capture_latest_frame()
        return Image(data=frame, format="jpeg")
    except Exception as err:
        err_msg = f"Cannot capture image frame. Details: {err}"
        get_logger_service().log_error_message(err_msg)
        raise ToolError(err_msg) from err


@mcp.tool(tags={"frame-info"})
async def get_latest_frame_info() -> dict[str, str | int | bool]:
    """Return availability and byte size for the latest cached camera frame."""
    redis_adapter = get_redis_adapter()
    frame = await redis_adapter.get_key(settings.CAMERA_FRAME_KEY)
    return {
        "available": frame is not None,
        "redis_key": settings.CAMERA_FRAME_KEY,
        "size_bytes": len(frame) if frame is not None else 0,
        "format": "jpeg",
    }


@mcp.tool(tags={"status"})
async def mcp_status() -> dict[str, str | bool]:
    """Return the status and purpose of this MCP service."""
    return {
        "healthy": True,
        "service": "camera-mcp-server",
        "purpose": "latest camera frame tools",
    }

