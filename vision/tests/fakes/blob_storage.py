


class FakeBlobStorage:
    def get_file(self, file_path: str) -> bytes | None:
        data = None
        try:
            with open(file_path, "rb") as file:
                data = file.read()
        except Exception as err:
            print(f"Could not read file, reason: {err}")
        return data

    def upload_file(self, file_content: str, file_path: str) -> None:
        blob = self._bucket.blob(file_path)
        blob.upload_from_string(
            data=file_content,
            content_type="image/jpeg"
        )
