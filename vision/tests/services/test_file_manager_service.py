import logging

from src.application.services.file_manager_service import FileManagerService
from src.application.services.logging_service import LoggerService



def test_can_get_file(fake_blob_storage):
    logger_service = LoggerService(level=logging.INFO)
    file_manager_service = FileManagerService(
        blob_storage_adapter=fake_blob_storage,
        logger_service=logger_service
    )
    file_path = "tests/fakes/fake_frame.jpeg"
    file = file_manager_service.get_frame(file_path)
    assert isinstance(file, bytes)
