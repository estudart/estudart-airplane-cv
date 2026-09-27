import asyncio

from src.dependencies import get_camera_streamer


def main() -> None:
    service = get_camera_streamer()
    asyncio.run(service.stream_frame())


if __name__ == "__main__":
    main()

