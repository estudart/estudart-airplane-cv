import logging

from openai import AsyncOpenAI

from src.infrastructure.database.database import Database
from src.application.services.camera_streamer import CameraStreamer
from src.application.services.logging_service import LoggerService
from src.config import settings
from src.infrastructure.camera_adapter import CameraAdapter
from src.infrastructure.image_prediction_adapter import ImagePredictorAdapter
from src.infrastructure.redis_adapter import RedisAdapter
from src.infrastructure.web_socket_adapter import WebSocketAdapter
from src.infrastructure.database.repositories.detection_repository import DetectionRepository
from src.infrastructure.gcs_adapter import GoogleCloudStorageAdapter
from src.application.services.file_manager_service import FileManagerService
from src.application.agents.camera_agent import CameraAgent
from src.application.agents.prompts.camera_agent_prompt import CAMERA_AGENT_SYSTEM_PROMPT
from src.application.services.camera_assistant_service import CameraAssistant
from src.application.services.web_socket_service import WebSocketService
from src.infrastructure.mcp_adapter import MCPAdapter

_database: Database | None = None
_camera_adapter: CameraAdapter | None = None
_web_socket_adapter: WebSocketAdapter | None = None
_camera_streamer: CameraStreamer | None = None
_image_predictor_adapter: ImagePredictorAdapter | None = None
_logger_service: LoggerService | None = None
_redis_adapter: RedisAdapter | None = None
_detection_repository: DetectionRepository | None = None
_google_cloud_storage_adapter: GoogleCloudStorageAdapter | None = None
_file_manager_service: FileManagerService | None = None
_mcp_adapter: MCPAdapter | None = None
_camera_agent: CameraAgent | None = None
_camera_assistant: CameraAssistant | None = None
_web_socket_service: WebSocketService | None = None



def get_database() -> Database:
    global _database
    if not _database:
        _database = Database(settings.DATABASE_URL)
    return _database

def get_logger_service() -> LoggerService:
    global _logger_service
    if not _logger_service:
        _logger_service = LoggerService(level=logging.INFO)
    return _logger_service

def get_camera_adapter() -> CameraAdapter:
    global _camera_adapter
    if not _camera_adapter:
        _camera_adapter = CameraAdapter(
            source=settings.CAMERA_SOURCE,
            width=settings.CAMERA_WIDTH,
            height=settings.CAMERA_HEIGHT,
            fps=settings.CAMERA_FPS,
        )
    return _camera_adapter

def get_web_socket_adapter() -> WebSocketAdapter:
    global _web_socket_adapter
    if not _web_socket_adapter:
        _web_socket_adapter = WebSocketAdapter(uri=settings.WS_SERVER_URL)
    return _web_socket_adapter

def get_image_predictor_adapter() -> ImagePredictorAdapter:
    global _image_predictor_adapter
    if not _image_predictor_adapter:
        _image_predictor_adapter = ImagePredictorAdapter(
            model_name=settings.MODEL_NAME,
            classes=settings.COUNT_CLASSES
        )
    return _image_predictor_adapter

def get_camera_streamer() -> CameraStreamer:
    global _camera_streamer
    if not _camera_streamer:
        _camera_streamer = CameraStreamer(
            logger_service=get_logger_service(),
            redis_adapter=get_redis_adapter(),
            camera_adapter=get_camera_adapter(),
            web_socket_adapter=get_web_socket_adapter(),
            image_predictor_adapter=get_image_predictor_adapter(),
            detection_repository=get_detection_repository(),
            gcs_adapter=get_google_cloud_storage_adapter(),
            should_predict=settings.SHOULD_PREDICT,
        )
    return _camera_streamer

def get_redis_adapter() -> RedisAdapter:
    global _redis_adapter
    if not _redis_adapter:
        _redis_adapter = RedisAdapter(logger_service=get_logger_service())
    return _redis_adapter

def get_detection_repository() -> DetectionRepository:
    global _detection_repository
    if not _detection_repository:
        _detection_repository = DetectionRepository(
            db=get_database(),
            logger_service=get_logger_service()
        )
    return _detection_repository

def get_google_cloud_storage_adapter() -> GoogleCloudStorageAdapter:
    global _google_cloud_storage_adapter
    if not _google_cloud_storage_adapter:
        _google_cloud_storage_adapter = GoogleCloudStorageAdapter(
            bucket_name=settings.BUCKET_NAME
        )
    return _google_cloud_storage_adapter

def get_file_manager_service() -> FileManagerService:
    global _file_manager_service
    if not _file_manager_service:
        _file_manager_service = FileManagerService(
            blob_storage_adapter=get_google_cloud_storage_adapter(),
            logger_service=get_logger_service()
        )
    return _file_manager_service

def get_mcp_adapter() -> MCPAdapter:
    global _mcp_adapter
    if not _mcp_adapter:
        # Imported here because the MCP server module wires its tools through
        # this file, and a module level import would close that cycle.
        from src.application.servers.mcp_server.mcp_server import mcp

        _mcp_adapter = MCPAdapter(mcp_server=mcp)
    return _mcp_adapter

async def get_camera_agent() -> CameraAgent:
    global _camera_agent
    if not _camera_agent:
        mcp_adapter = get_mcp_adapter()
        mcp_tools = await mcp_adapter.list_tools()
        _camera_agent = CameraAgent(
            system_prompt=CAMERA_AGENT_SYSTEM_PROMPT,
            model=settings.MODEL,
            llm_client_factory=lambda: AsyncOpenAI(api_key=settings.OPENAI_API_KEY),
            mcp_adapter=mcp_adapter,
            mcp_tools=[
                tool for tool in mcp_tools
                if tool["name"] in settings.CAMERA_AGENT_TOOLS
            ],
            logger_service=get_logger_service(),
        )
    return _camera_agent

async def get_camera_assistant() -> CameraAssistant:
    global _camera_assistant
    if not _camera_assistant:
        _camera_assistant = CameraAssistant(camera_agent=await get_camera_agent())
    return _camera_assistant

async def get_web_socket_service() -> WebSocketService:
    global _web_socket_service
    if not _web_socket_service:
        _web_socket_service = WebSocketService(
            camera_assistant=await get_camera_assistant(),
            logger_service=get_logger_service(),
        )
    return _web_socket_service
