# estudart-airplane-cv

Computer-vision study lab derived from `estudart-mcp-robot`. It preserves the original service boundaries, WebSocket chat, MCP adapter, conversational agent, camera flow, and browser speech output while removing the physical robot controls.

## Architecture

```text
macOS webcam -> native camera-streamer --WebSocket--> backend -> CameraStream
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

On Linux/Raspberry, the same camera-streamer can run in Docker through the hardware override. Only the adapter placement changes; the frame, Redis, MCP, backend, and frontend protocols stay the same.

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

`CameraStream` subscribes with `?subscribeType=camera-data-consumer&detected=true`. `CameraChat` talks to `camera-agent` over a separate WebSocket connection.

## Camera agent

The backend keeps the original application/infrastructure/presentation split. `CameraAgent` receives only these MCP tools:

- `capture_image`: sends the latest Redis JPEG to the multimodal model.
- `get_latest_frame_info`: reports frame availability and size.
- `mcp_status`: reports the camera MCP service status.

Speech is a frontend concern in this Mac MVP. When a new agent `response` arrives over WebSocket, `CameraChat` creates one `SpeechSynthesisUtterance` and the browser plays it through the Mac default speaker. The backend does not call a speaker REST endpoint.

## Configuration by service

There is no root `.env.example`, `.gitignore`, or `.dockerignore`. Each service owns its files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp vision/.env.example vision/.env
```

Set `OPENAI_API_KEY` in `backend/.env`. The Compose stack reads `backend/.env` and `vision/.env` directly. The native streamer reads `vision/.env` through `pydantic-settings`.

Useful vision values:

```dotenv
CAMERA_SOURCE=0
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FPS=15
MODEL_NAME=yolo11n.pt
PREDICTION_EVERY_N_FRAMES=5
```

## Start on macOS

Docker Desktop cannot expose the built-in webcam as `/dev/video0`. The normal entry point manages the Docker services and native camera streamer together:

```bash
make up
```

`make up` starts Compose in detached mode, runs the camera adapter natively with macOS camera permission through `uv run`, follows the container logs, and stops both lifecycles on `Ctrl+C`. `make dev` is an alias for the same flow.

For camera-only debugging, keep the Docker core running and use `make camera-mac` in another terminal:

```bash
make camera-mac
```

The native process uses `uv run`, opens `CAMERA_SOURCE` on macOS, publishes frames to `ws://localhost:8080`, and stores the latest JPEG in Redis at `localhost:6379`.

Open:

- Camera and chat: <http://localhost:5173>
- Backend health: <http://localhost:8080/health>
- MCP endpoint: <http://localhost:8000/mcp>
- Vision health: <http://localhost:8000/api/health>

Ask “Describe what you see now.” The agent must call `capture_image`, answer in the chat, and the browser speaks that new response through the Mac default speaker.

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
make check-backend
make check-frontend
make check-python
make check-exclusions
make check-readme
docker compose config
docker compose build
```
