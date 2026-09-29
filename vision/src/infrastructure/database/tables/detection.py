from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.database import Base



class DetectionTable(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    detected_object: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
