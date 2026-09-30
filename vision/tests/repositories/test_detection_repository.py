import logging

from src.infrastructure.database.repositories.detection_repository import DetectionRepository
from src.application.services.logging_service import LoggerService



def test_can_store_new_detection_value(fake_db) -> None:
    logger_service = LoggerService(level=logging.DEBUG)
    detection_repository = DetectionRepository(
        db=fake_db._db,
        logger_service=logger_service
    )
    assert detection_repository.create("airplane", 0.89)
