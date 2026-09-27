from src.application.servers.mcp_server import mcp_server


class FakeRedisAdapter:
    async def get_key(self, key: str):
        assert key == "camera:latest"
        return b"latest-jpeg"


async def test_capture_latest_frame_reads_shared_redis_key(monkeypatch) -> None:
    monkeypatch.setattr(
        mcp_server,
        "get_redis_adapter",
        lambda: FakeRedisAdapter(),
    )

    assert await mcp_server._capture_latest_frame() == b"latest-jpeg"
