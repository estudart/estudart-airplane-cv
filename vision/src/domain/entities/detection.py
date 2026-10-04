from dataclasses import dataclass


@dataclass
class Detection:
    detected_object: str
    confidence: float
