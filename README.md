# estudart-airplane-cv

Computer-vision study lab derived from `estudart-mcp-robot`. It preserves the original service boundaries, WebSocket chat, MCP adapter, conversational agent, camera flow, and REST speaker integration while removing the physical robot controls.

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
                                   REST POST /api/speak
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

The speaker is intentionally not an MCP tool. After the agent answers, the backend sends that exact final chat message to the vision REST route `POST /api/speak`, matching the robot project flow.

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
SPEAKER_DEVICE=plughw:CARD=Device,DEV=0
SPEAKER_ENABLED=true
```

## Start on macOS

Docker Desktop cannot expose the built-in webcam as `/dev/video0`. The normal development entry point manages the Docker services and native camera streamer together:

```bash
make dev
```

`make dev` starts Compose in detached mode, runs the camera adapter natively with macOS camera permission, follows the container logs, and stops both lifecycles on `Ctrl+C`.

For two-terminal debugging, `make up` runs only the Docker core in the foreground and `make camera-mac` runs only the native streamer:

```bash
# terminal 1
make up

# terminal 2
make camera-mac
```

The native process uses `uv run`, opens `CAMERA_SOURCE` on macOS, publishes frames to `ws://localhost:8080`, and stores the latest JPEG in Redis at `localhost:6379`.

Open:

- Camera and chat: <http://localhost:5173>
- Backend health: <http://localhost:8080/health>
- MCP endpoint: <http://localhost:8000/mcp>
- Vision health: <http://localhost:8000/api/health>

Ask “Describe what you see now.” The agent must call `capture_image`, answer in the chat, and send the same final answer to the speaker REST route.

Stop the Docker services with `make down`. Stop the native camera streamer with `Ctrl+C`.

## Start on Linux/Raspberry

The hardware target enables the camera container at `/dev/video0` and the MCP speaker at `/dev/snd`:

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
