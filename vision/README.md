# Vision services

The `vision` package contains the camera streamer and the FastAPI/MCP server. They share the same application, infrastructure, and presentation layers.

- `camera-streamer` reads `CAMERA_SOURCE`, runs YOLO detection, stores the latest rendered JPEG in Redis, and publishes it over WebSocket.
- `vision` serves REST routes, the camera WebSocket, and the FastMCP camera tools from one FastAPI app on port `8000`.

On macOS, `make camera-mac` runs the streamer natively so OpenCV can access the host webcam. Redis, Postgres, the vision server, and the frontend remain in Docker. On Linux/Raspberry, `make up-hardware` runs the same streamer in Docker with the camera device mapping.

## Routes and tools

FastAPI routes:

- `GET /api/health`
- `POST /api/camera-assistant` — ask the camera agent over request/response
- `WS /ws` — the camera socket: frames in, frames out, agent answers

MCP tools:

- `capture_image`
- `get_latest_frame_info`
- `mcp_status`

The WebSocket route is registered before the MCP app is mounted at `/`, so `/ws` and `/api/*` match first and everything else falls through to `/mcp`.

## Camera socket protocol

The streamer is the producer, the browser is the consumer, and both use the same `/ws` endpoint.

```json
// streamer -> server
{"type": "camera-frame", "message": "<base64 jpeg>"}

// server -> every consumer that subscribed with
// ?subscribeType=camera-data-consumer&detected=true
{"type": "camera-frame", "frame": "<base64 jpeg>"}

// browser -> server
{"type": "camera-agent", "question": "Describe what you see now."}

// server -> the asking connection only
{"type": "response", "message": "...", "agent": "camera-agent"}

// server -> the asking connection, on any failure
{"type": "error", "message": "..."}
```

## Camera agent

`CameraAgent` runs an OpenAI chat loop and reaches the camera tools through `MCPAdapter`, an in-process MCP client. The tools stay behind the MCP protocol even though the server object lives in the same app, so the agent sees exactly what a remote MCP client would see.

`capture_image` answers with an image content block. A chat `tool` message carries text only, so the agent replays the frame as an extra user message holding a `data:image/jpeg;base64,...` URL.

The chat client is built on first use. Without `OPENAI_API_KEY` the camera stream still works and only the chat answers with an `error` message.

Agent settings in `.env`:

```dotenv
OPENAI_API_KEY=
MODEL=gpt-4o-mini
```

## uv workflow

```bash
cp .env.example .env
uv sync --frozen --extra dev
uv run pytest
uv run python -m compileall -q src
```

Both vision Dockerfiles install dependencies from `uv.lock` with `uv sync --frozen --no-install-project`. Torch and torchvision come from the explicit `pytorch-cpu` index; CUDA/NVIDIA packages are excluded.
