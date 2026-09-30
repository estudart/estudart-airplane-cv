import logging

from src.application.services.logging_service import LoggerService
from src.infrastructure.redis_adapter import RedisAdapter


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}

    async def set(self, key: str, value: bytes) -> None:
        self.values[key] = value

    async def get(self, key: str):
        return self.values.get(key)


async def test_redis_adapter_stores_latest_frame_bytes() -> None:
    adapter = RedisAdapter(LoggerService(level=logging.CRITICAL))
    adapter._db = FakeRedis()

    await adapter.set_key("camera:latest", b"jpeg-bytes")

    assert await adapter.get_key("camera:latest") == b"jpeg-bytes"


async def test_redis_adapter_returns_none_for_missing_frame() -> None:
    adapter = RedisAdapter(LoggerService(level=logging.CRITICAL))
    adapter._db = FakeRedis()

    assert await adapter.get_key("camera:latest") is None

