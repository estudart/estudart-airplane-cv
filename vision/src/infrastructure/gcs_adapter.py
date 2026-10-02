from google.cloud import storage

from src.config import settings

class GoogleCloudStorageAdapter:
    def __init__(self):
        self._client = storage.Client()
        self._bucket = self._client.bucket(settings.BUCKET_NAME)

    def get_file(self, file_path: str) -> bytes:
        blob = self._bucket.blob(file_path)
        return blob.download_as_bytes() 

    def upload_file(self, file_content: str, file_path: str) -> None:
        blob = self._bucket.blob(file_path)
        blob.upload_from_string(
            data=file_content,
            content_type="image/jpeg"
        )
