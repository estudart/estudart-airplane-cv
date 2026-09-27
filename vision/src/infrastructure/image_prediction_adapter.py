from ultralytics import YOLO


class ImagePredictorAdapter:
    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model: YOLO | None = None

    def predict_image(self, frame):
        if self._model is None:
            self._model = YOLO(self._model_name)
        return self._model.predict(frame, show=False, verbose=False)[0]

