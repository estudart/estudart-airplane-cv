from google.cloud import storage

from src.config import settings
from src.application.services.logging_service import LoggerService

class GoogleCloudStorageAdapter:
    def __init__(self, bucket_name: str, logger_service: LoggerService):
        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket_name)
        self._logger_service = logger_service

    def get_file(self, file_path: str) -> bytes | None:
        try:
            blob = self._bucket.blob(file_path)
            return blob.download_as_bytes()
        except Exception as err:
            self._logger_service.log_error_message(err)
            return None

    def upload_file(self, file_content: str, file_path: str) -> bool:
        try:
            blob = self._bucket.blob(file_path)
            blob.upload_from_string(
                data=file_content,
                content_type="image/jpeg"
            )
            return True
        except Exception as err:
            self._logger_service.log_error_message(err)
            return False
