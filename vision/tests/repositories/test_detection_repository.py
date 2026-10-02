import logging

from src.infrastructure.database.repositories.detection_repository import DetectionRepository
from src.application.services.logging_service import LoggerService



def test_can_store_new_detection_value(fake_db) -> None:
    logger_service = LoggerService(level=logging.DEBUG)
    detection_repository = DetectionRepository(
        db=fake_db._db,
        logger_service=logger_service
    )
    new_detection = detection_repository.create("airplane", 0.89)
    assert new_detection.detected_object == "airplane"

def test_can_get_detection(fake_db) -> None:
    logger_service = LoggerService(level=logging.DEBUG)
    detection_repository = DetectionRepository(
        db=fake_db._db,
        logger_service=logger_service
    )
    new_detection = detection_repository.create("airplane", 0.89)
    detection_id = new_detection.id

    assert detection_repository.get_by_id(detection_id).id == detection_id

def test_can_get_all_detections(fake_db) -> None:
    logger_service = LoggerService(level=logging.DEBUG)
    detection_repository = DetectionRepository(
        db=fake_db._db,
        logger_service=logger_service
    )

    new_detection_1 = detection_repository.create("airplane", 0.89)
    new_detection_2 = detection_repository.create("bed", 0.89)

    all_detections = detection_repository.get_all()

    assert len(all_detections) == 2
