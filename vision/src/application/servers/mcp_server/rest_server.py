from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastmcp.utilities.lifespan import combine_lifespans

from src.application.servers.mcp_server.mcp_server import mcp
from src.presentation.routes.health_route import health_router
from src.infrastructure.database.tables.detection import Detection
from src.dependencies import get_database
from src.config import settings

@asynccontextmanager
async def app_lifespan(_app: FastAPI):
    print("Starting up the app...")
    yield
    print("Shutting down the app...")

mcp_app = mcp.http_app()

app = FastAPI(
    title="Camera MCP API",
    lifespan=combine_lifespans(app_lifespan, mcp_app.lifespan),
)

app.include_router(health_router)

print("Starting MCP Server...")

app.mount("/", mcp_app)
