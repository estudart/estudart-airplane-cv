import logging

from src.infrastructure.database.database import Database
from src.application.services.camera_streamer import CameraStreamer
from src.application.services.logging_service import LoggerService
from src.config import settings
from src.infrastructure.camera_adapter import CameraAdapter
from src.infrastructure.image_prediction_adapter import ImagePredictorAdapter
from src.infrastructure.redis_adapter import RedisAdapter
from src.infrastructure.web_socket_adapter import WebSocketAdapter
from src.infrastructure.database.repositories.detection_repository import DetectionRepository

_database: Database | None = None
_camera_adapter: CameraAdapter | None = None
_web_socket_adapter: WebSocketAdapter | None = None
_camera_streamer: CameraStreamer | None = None
_image_predictor_adapter: ImagePredictorAdapter | None = None
_logger_service: LoggerService | None = None
_redis_adapter: RedisAdapter | None = None
_detection_repository: DetectionRepository | None = None


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
