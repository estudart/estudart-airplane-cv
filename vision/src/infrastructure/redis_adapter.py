import pickle

import redis.asyncio as redis

from src.application.services.logging_service import LoggerService
from src.config import settings


class RedisAdapter:
    def __init__(self, logger_service: LoggerService):
        self._logger_service = logger_service
        self._host = settings.REDIS_HOST
        self._port = settings.REDIS_PORT
        self._db: redis.Redis | None = None

    async def _create_connection(self):
        self._db = redis.Redis(
            host=self._host,
            port=self._port,
            ssl=False,
        )
        await self._db.ping()
        self._logger_service.log_info_message(
            f"Connection with Redis was established, host: {self._host}:{self._port}"
        )
        return self._db

    async def set_key(self, key: str, value: bytes) -> None:
        if not self._db:
            await self._create_connection()

        await self._db.set(key, pickle.dumps(value))
        self._logger_service.log_debug_message(f"New key set to Redis, key: {key}")

    async def get_key(self, key: str) -> bytes | None:
        if not self._db:
            await self._create_connection()

        value = await self._db.get(key)
        if value is None:
            return None

        self._logger_service.log_debug_message(
            f"New value retrieved from Redis, key: {key}"
        )
        return pickle.loads(value)

