from src.infrastructure.camera_adapter import CameraAdapter


def test_camera_source_number_is_converted_to_device_index() -> None:
    assert CameraAdapter.parse_source("0") == 0


def test_camera_source_url_is_preserved() -> None:
    source = "http://host.docker.internal:8081/camera.mjpg"
    assert CameraAdapter.parse_source(source) == source

