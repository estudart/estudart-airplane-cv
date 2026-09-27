from src.infrastructure.speech_adapter import SpeechAdapter
from src.application.services.logging_service import LoggerService


class SpeakService:
    def __init__(
        self,
        logger_service: LoggerService,
        speech_adapter: SpeechAdapter,
    ) -> None:
        self._logger_service = logger_service
        self._speech_adapter = speech_adapter
    
    def speak(self, text: str) -> bool:
        try:
            self._speech_adapter.speak(text=text)
            return True
        except Exception as err:
            self._logger_service._logger.info(
                f"Could not play audio, reason: {err}"
            )
