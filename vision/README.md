# Vision services

The `vision` package contains the camera streamer and MCP/FastAPI server. They share the same application, infrastructure, and presentation layers.

- `camera-streamer` reads `CAMERA_SOURCE`, runs YOLO detection, stores the latest rendered JPEG in Redis, and publishes it over WebSocket.
- `mcp-server` exposes FastMCP camera tools plus FastAPI presentation routes built with `APIRouter`.

On macOS, `make camera-mac` runs the streamer natively so OpenCV can access the host webcam. Redis, MCP, backend, and frontend remain in Docker. On Linux/Raspberry, `make up-hardware` runs the same streamer in Docker with the camera device mapping.

## Routes and tools

FastAPI routes:

- `GET /api/health`
- `POST /api/speak?text=...`

MCP tools:

- `capture_image`
- `get_latest_frame_info`
- `mcp_status`

The speaker remains a REST integration called by the backend after the agent produces its final message. It is not available to the agent as an MCP tool.

## uv workflow

```bash
cp .env.example .env
uv sync --frozen --extra dev
uv run pytest
uv run python -m compileall -q src
```

Both vision Dockerfiles install dependencies from `uv.lock` with `uv sync --frozen --no-install-project`. Torch and torchvision come from the explicit `pytorch-cpu` index; CUDA/NVIDIA packages are excluded.
