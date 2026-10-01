from datetime import datetime

from sqlalchemy import select

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

    def get_all(self) -> Detection | None:
        try:
            with self._db.session() as session:
                results = session.execute(select(Detection)).all()
            return results
        except Exception as err:
            self._logger_service.log_error_message(
                f"Could not get detection, reason: {err}"
            )
            return None

    def get_by_id(self, detection_id: int) -> Detection | None:
        try:
            with self._db.session() as session:
                statement = (
                    select(Detection)
                    .where(Detection.id == detection_id)
                )
                result = session.scalars(statement).one()
            return result
        except Exception as err:
            self._logger_service.log_error_message(
                f"Could not get detection, reason: {err}"
            )
            return None

    def create(
        self,
        detected_object: str,
        confidence: float
    ) -> Detection:
        try:
            current_date = datetime.now()
            new_detection = Detection(
                detected_object=detected_object,
                confidence=confidence,
                storage_path=(
                    f"detection/frames/{detected_object}/"
                    f"{current_date.day}-{current_date.month}-{current_date.year}/"
                    f"{current_date.hour}-{current_date.minute}-{current_date.second}"
                )
            )
            with self._db.session() as session:
                session.add(new_detection)
            return new_detection
        except Exception as err:
            self._logger_service.log_error_message(
                f"Could not add new detection, reason: {err}"
            )
            return None

    def update(self):
        pass
