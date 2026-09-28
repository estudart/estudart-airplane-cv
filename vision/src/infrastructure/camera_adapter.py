import base64

import cv2 as cv


class CameraAdapter:
    def __init__(
        self,
        source: str = "0",
        width: int = 1280,
        height: int = 720,
        fps: int = 15,
    ) -> None:
        self._source = self.parse_source(source)
        self._width = width
        self._height = height
        self._fps = fps
        self._cap: cv.VideoCapture | None = None

        self._set_capture()

    @staticmethod
    def parse_source(source: str):
        return int(source) if source.isdigit() else source

    def _set_capture(self) -> cv.VideoCapture:
        if self._cap is None:
            self._cap = cv.VideoCapture(self._source)
            self._cap.set(cv.CAP_PROP_FRAME_WIDTH, self._width)
            self._cap.set(cv.CAP_PROP_FRAME_HEIGHT, self._height)
            self._cap.set(cv.CAP_PROP_FPS, self._fps)

        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open camera source: {self._source}")

    def get_writer(self, path: str):
        return cv.VideoWriter(
            path,
            cv.VideoWriter_fourcc(*"mp4v"),
            self._fps,
            (self._width, self._height)
        )

    def get_frame(self):
        received, frame = self._cap.read()
        if not received or frame is None:
            raise RuntimeError(f"Could not read camera source: {self._source}")
        return frame

    def read_image(self, path: str):
        return cv.imread(path)

    def save_image(self, path, frame):
        cv.imwrite(path, frame)

    def from_frame_to_b64(self, frame) -> str:
        encoded, buffer = cv.imencode(".jpg", frame)
        if not encoded:
            raise RuntimeError("Could not encode camera frame")
        return base64.b64encode(buffer).decode("utf-8")

    def from_frame_to_bytes(self, frame) -> bytes:
        encoded, buffer = cv.imencode(".jpg", frame)
        if not encoded:
            raise RuntimeError("Could not encode camera frame")
        return buffer.tobytes()

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def close_all_windows(self):
        cv.destroyAllWindows()

