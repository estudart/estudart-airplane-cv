import logging

from src.application.services.camera_streamer import CameraStreamer
from src.application.services.logging_service import LoggerService
from src.application.services.speak_service import SpeakService
from src.config import settings
from src.infrastructure.camera_adapter import CameraAdapter
from src.infrastructure.image_prediction_adapter import ImagePredictorAdapter
from src.infrastructure.redis_adapter import RedisAdapter
from src.infrastructure.speech_adapter import SpeechAdapter
from src.infrastructure.web_socket_adapter import WebSocketAdapter


_camera_adapter: CameraAdapter | None = None
_web_socket_adapter: WebSocketAdapter | None = None
_camera_streamer: CameraStreamer | None = None
_image_predictor_adapter: ImagePredictorAdapter | None = None
_logger_service: LoggerService | None = None
_redis_adapter: RedisAdapter | None = None
_speech_adapter: SpeechAdapter | None = None
_speak_service: SpeakService | None = None


def get_logger_service() -> LoggerService:
    global _logger_service
    if not _logger_service:
        _logger_service = LoggerService(level=logging.INFO)
    return _logger_service


def get_speech_adapter() -> SpeechAdapter:
    global _speech_adapter
    if not _speech_adapter:
        _speech_adapter = SpeechAdapter(
            device=settings.SPEAKER_DEVICE,
            enabled=settings.SPEAKER_ENABLED,
        )
    return _speech_adapter


def get_speak_service() -> SpeakService:
    global _speak_service
    if not _speak_service:
        _speak_service = SpeakService(
            logger_service=get_logger_service(),
            speech_adapter=get_speech_adapter(),
        )
    return _speak_service


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
            model_name=settings.MODEL_NAME
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
            should_predict=settings.SHOULD_PREDICT,
        )
    return _camera_streamer


def get_redis_adapter() -> RedisAdapter:
    global _redis_adapter
    if not _redis_adapter:
        _redis_adapter = RedisAdapter(logger_service=get_logger_service())
    return _redis_adapter

