from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp.utilities.lifespan import combine_lifespans

from src.application.servers.mcp_server.mcp_server import mcp
from src.presentation.routes.camera_agent_route import camera_agent_router
from src.presentation.routes.camera_socket_route import camera_socket_router
from src.presentation.routes.health_route import health_router
from src.infrastructure.database.tables.detection import Detection
from src.dependencies import get_database

@asynccontextmanager
async def app_lifespan(_app: FastAPI):
    database = get_database()
    print("Starting up the app...")
    database._create_all()
    try:
        yield
    finally:
        print("Shutting down the app...")
        database.dispose()

mcp_app = mcp.http_app()

app = FastAPI(
    title="Camera MCP API",
    lifespan=combine_lifespans(app_lifespan, mcp_app.lifespan),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(camera_agent_router)
app.include_router(camera_socket_router)

print("Starting MCP Server...")

# Mounted last so the REST and WebSocket routes above win the match.
app.mount("/", mcp_app)
