from src.infrastructure.gcs_adapter import GoogleCloudStorageAdapter
from src.application.services.logging_service import LoggerService



class FileManagerService:
    def __init__(
        self,
        blob_storage_adapter: GoogleCloudStorageAdapter,
        logger_service: LoggerService
    ) -> None:
        self._blob_storage_adapter = blob_storage_adapter
        self._logger_service = logger_service

    def get_frame(self, file_path: str) -> bytes:
        return self._blob_storage_adapter.get_file(file_path)
    
    def upload_file(self, file_content: str, file_path: str) -> bool:
        return self._blob_storage_adapter.upload_file(
            file_content=file_content,
            file_path=file_path
        )
