import logging


class LoggerService:
    def __init__(self, level):
        self._console_handler = logging.StreamHandler()
        self._console_handler.setFormatter(
            logging.Formatter("{levelname} - {message}", style="{")
        )
        self._logger = logging.getLogger("Airplane Camera MCP Server")
        if not self._logger.handlers:
            self._logger.addHandler(self._console_handler)
        self._level = level
        self._logger.setLevel(self._level)

    def log_debug_message(self, message: str) -> None:
        self._logger.debug(message)

    def log_info_message(self, message: str) -> None:
        self._logger.info(message)

    def log_error_message(self, message: str) -> None:
        self._logger.error(message)

