import asyncio

from src.application.services.logging_service import LoggerService
from src.config import settings
from src.infrastructure.camera_adapter import CameraAdapter
from src.infrastructure.image_prediction_adapter import ImagePredictorAdapter
from src.infrastructure.redis_adapter import RedisAdapter
from src.infrastructure.web_socket_adapter import WebSocketAdapter
from src.infrastructure.database.repositories.detection_repository import DetectionRepository
from src.infrastructure.gcs_adapter import GoogleCloudStorageAdapter


class CameraStreamer:
    def __init__(
        self,
        logger_service: LoggerService,
        redis_adapter: RedisAdapter,
        camera_adapter: CameraAdapter,
        web_socket_adapter: WebSocketAdapter,
        image_predictor_adapter: ImagePredictorAdapter,
        detection_repository: DetectionRepository,
        gcs_adapter: GoogleCloudStorageAdapter,
        should_predict: bool,
    ) -> None:
        self._logger_service = logger_service
        self._redis_adapter = redis_adapter
        self._camera_adapter = camera_adapter
        self._web_socket_adapter = web_socket_adapter
        self._image_predictor_adapter = image_predictor_adapter
        self._gcs_adapter = gcs_adapter
        self._detection_repository = detection_repository
        self._last_result = None
        self._count_frame = 0
        self._should_predict = should_predict

    async def connect_stream(self):
        await self._web_socket_adapter.connect()
        self._logger_service.log_info_message("Connection established")

    async def stream_frame(self):
        await self.connect_stream()
        await self._redis_adapter._create_connection()

        self._logger_service.log_info_message("Starting camera streaming...")

        while True:
            try:
                raw_frame = self._camera_adapter.get_frame()

                self._last_result, counted_objects = self._image_predictor_adapter.count_objects(
                    frame=raw_frame
                )

                frame = self._last_result.plot_im

                for counted_object in counted_objects:
                    new_detection = self._detection_repository.create(
                        detected_object=counted_object.detected_object,
                        confidence=counted_object.confidence
                    )

                    self._gcs_adapter.upload_file(
                        file_content=self._camera_adapter.from_frame_to_bytes(raw_frame),
                        file_path=new_detection.storage_path
                    )

                await self._redis_adapter.set_key(
                    key=settings.CAMERA_FRAME_KEY,
                    value=self._camera_adapter.from_frame_to_bytes(frame),
                )

                await self._web_socket_adapter.send_message(
                    msg_type="camera-frame",
                    message=self._camera_adapter.from_frame_to_b64(frame),
                )

            except Exception as err:
                self._logger_service.log_error_message(
                    f"Could not stream frame, reason: {err}"
                )
                await asyncio.sleep(5)

