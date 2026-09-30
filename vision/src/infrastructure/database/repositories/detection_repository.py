from src.infrastructure.database.database import Database
from src.infrastructure.database.tables.detection import Detection
from src.application.services.logging_service import LoggerService


class DetectionRepository:
    def __init__(
        self,
        db: Database,
        logger_service: LoggerService
    ) -> None:
        self._db = db
        self._logger_service = logger_service
    
    def to_domain(self):
        pass

    def get_all(self):
        with self._db.session() as session:
            results = s.execute(select(Detection)).all()
        return results

    def create(
        self,
        detected_object: str,
        confidence: float
    ) -> bool:
        try:
            new_detection = Detection(
                detected_object=detected_object,
                confidence=confidence
            )
            with self._db.session() as session:
                session.add(new_detection)
            return True
        except Exception as err:
            self._logger_service.log_error_message(
                f"Could not add new detection, reason: {err}"
            )
            return False

    def update(self):
        pass
