from ultralytics import YOLO, solutions


class ImagePredictorAdapter:
    def __init__(
        self, 
        model_name: str,
        width: int = 1280,
        height: int = 720,
    ):
        self._model_name = model_name
        self._model: YOLO | None = None
        self._width = width
        self._height = height
        self._object_counter = solutions.ObjectCounter(
            show=True,
            region=[(600, 100), (600, 600)],
            model=self._model,
            classes=[4],
        )

    def count_objects(self, frame):
        if self._model is None:
            self._model = YOLO(self._model_name)
        return self._object_counter(frame)

    def predict_image(self, frame):
        if self._model is None:
            self._model = YOLO(self._model_name)
        return self._model.predict(frame, show=False, verbose=False)[0]

