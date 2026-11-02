# estudart-airplane-cv

Computer-vision study lab derived from `estudart-mcp-robot`. It keeps the WebSocket chat, MCP camera tools, conversational agent, camera flow, and browser speech output, with a React frontend and a single Python backend.

## Architecture

```text
macOS webcam -> native camera-streamer --WebSocket--> vision -> CameraStream
                         |                       |
                         v                       v
                   Docker Redis             CameraChat
                         |                       |
                         v                       v
              FastMCP camera tools <- CameraAgent response
                                                 |
                                                 v
                              browser speechSynthesis
                                      |
                                      v
                              Mac default speaker
```

`vision` is one FastAPI app on port `8000` serving three surfaces:

- REST: `GET /api/health`, `POST /api/camera-assistant`
- WebSocket: `WS /ws`, the camera socket shared by the streamer and the browser
- MCP: `/mcp`, the FastMCP camera tools

On Linux/Raspberry, the same camera-streamer can run in Docker through the hardware override. Only the adapter placement changes; the frame, Redis, MCP, and WebSocket protocols stay the same.

The streamer publishes the rendered JPEG through the existing WebSocket shape and stores the same last frame at `camera:latest` in Redis:

```json
{"type":"camera-frame","frame":"<base64 jpeg>"}
```

The frontend has one page, `CameraView`, composed from two components:

```text
CameraView
├── CameraStream
└── CameraChat
```

`CameraStream` subscribes with `?subscribeType=camera-data-consumer&detected=true`. `CameraChat` talks to `camera-agent` over a separate WebSocket connection. Both read their endpoint from `src/services/vision-socket.ts`.

## Camera agent

The agent lives in `vision` and keeps the application/infrastructure/presentation split. `CameraAgent` reaches the camera tools through an in-process MCP client, so the tools stay behind the MCP protocol:

- `capture_image`: sends the latest Redis JPEG to the multimodal model.
- `get_latest_frame_info`: reports frame availability and size.
- `mcp_status`: reports the camera MCP service status.

The browser chat asks over the WebSocket, because the answer belongs on the connection that already carries the frames. `POST /api/camera-assistant` is the request/response door to the same agent.

Speech is a frontend concern in this Mac MVP. When a new agent `response` arrives over WebSocket, `CameraChat` creates one `SpeechSynthesisUtterance` and the browser plays it through the Mac default speaker. The backend does not call a speaker REST endpoint.

## Configuration by service

There is no root `.env.example`, `.gitignore`, or `.dockerignore`. Each service owns its files:

```bash
cp frontend/.env.example frontend/.env
cp vision/.env.example vision/.env
```

Set `OPENAI_API_KEY` in `vision/.env`. The Compose stack reads `vision/.env` directly, and the native streamer reads it through `pydantic-settings`. Without the key the camera stream still runs and only the chat answers with an error.

Useful vision values:

```dotenv
CAMERA_SOURCE=0
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FPS=15
MODEL_NAME=yolo11n.pt
PREDICTION_EVERY_N_FRAMES=5
MODEL=gpt-4o-mini
```

The frontend points at the camera socket with one value:

```dotenv
VITE_VISION_URL=ws://localhost:8000/ws
```

## Start on macOS

Docker Desktop cannot expose the built-in webcam as `/dev/video0`. The normal entry point manages the Docker services and native camera streamer together:

```bash
make up
```

`make up` starts Compose in detached mode, runs the camera adapter natively with macOS camera permission through `uv run`, follows the container logs, and stops both lifecycles on `Ctrl+C`. `make dev` is an alias for the same flow.

## Hot reload while you code

`make dev-reload` runs the code you edit on the host and keeps only Redis and Postgres in Docker:

```bash
make dev-reload
```

- `vision` runs under `uvicorn --reload --reload-dir src`, so a Python save restarts the server.
- `frontend` runs under the vite dev server on <http://localhost:5173>, so a React save hot-reloads the page.

`Ctrl+C` stops both and the two containers. `make dev-api` and `make dev-web` run one side alone, and `VISION_PORT`, `FRONTEND_PORT`, and `VISION_URL` override the defaults.

The camera is a third process, because it needs host webcam permission:

```bash
make camera-mac
```

A `--reload` restart drops the streamer's WebSocket and it does not reconnect on its own, so restart `make camera-mac` after a backend save if the frames stop.

## Two-terminal debugging

For two-terminal debugging, run the Docker core directly and the native camera separately:

```bash
# terminal 1
docker compose up --build

# terminal 2
make camera-mac
```

The native process uses `uv run`, opens `CAMERA_SOURCE` on macOS, publishes frames to `ws://localhost:8000/ws`, and stores the latest JPEG in Redis at `localhost:6379`.

Open:

- Camera and chat: <http://localhost:5173>
- Vision health: <http://localhost:8000/api/health>
- API docs: <http://localhost:8000/docs>
- MCP endpoint: <http://localhost:8000/mcp>

Ask “Describe what you see now.” The agent must call `capture_image`, answer in the chat, and the browser speaks that new response through the Mac default speaker.

The same question without a browser:

```bash
curl -X POST http://localhost:8000/api/camera-assistant \
  -H 'Content-Type: application/json' \
  -d '{"question":"Describe what you see now."}'
```

Stop the complete `make up` flow with `Ctrl+C`. The cleanup stops both the native camera streamer and Docker services. `make down` remains available for a detached stack.

## Start on Linux/Raspberry

The hardware target enables the camera container at `/dev/video0`:

```bash
make up-hardware
```

Override the camera device when needed:

```bash
CAMERA_DEVICE=/dev/video2 make up-hardware
```

## Development checks

The `vision` service uses `uv` and commits `uv.lock`. Torch and torchvision are locked to the explicit `pytorch-cpu` index, matching the source project and preventing CUDA/NVIDIA dependency downloads.

```bash
make check-frontend
make check-python
make check-exclusions
make check-readme
docker compose config
docker compose build
```
