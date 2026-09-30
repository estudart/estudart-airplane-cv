import logging

from src.infrastructure.database.tables.detection import Detection
from src.infrastructure.database.repositories.detection_repository import DetectionRepository
from src.infrastructure.database.database import Database, Base
from src.application.services.logging_service import LoggerService



def test_can_store_new_detection_value() -> None:
    db = Database(url="sqlite:///test.db")
    Base.metadata.create_all(db._engine)
    logger_service = LoggerService(level=logging.DEBUG)
    detection_repository = DetectionRepository(
        db=db,
        logger_service=logger_service
    )
    assert detection_repository.create("airplane", 0.89)
