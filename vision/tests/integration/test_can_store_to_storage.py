from src.infrastructure.gcs_adapter import GoogleCloudStorageAdapter
from src.infrastructure.camera_adapter import CameraAdapter
from src.config import settings


def test_can_store_to_storage() -> None:
    camera_adapter = CameraAdapter()
    gcs_adapter = GoogleCloudStorageAdapter(settings.BUCKET_NAME)
    
    file_path = "integration-tests/frames"
    frame = camera_adapter.get_frame()

    gcs_adapter.upload_file(
        file_content=camera_adapter.from_frame_to_bytes(frame),
        file_path=file_path
    )
    stored_file = gcs_adapter.get_file(file_path)

    assert isinstance(stored_file, bytes)
