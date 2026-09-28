from ultralytics import YOLO, solutions


class ImagePredictorAdapter:
    def __init__(
        self,
        model_name: str,
        width: int = 1280,
        height: int = 720,
        show: bool = False,
        classes: list = [4]
    ):
        self._model = YOLO(model_name)
        self._width = width
        self._height = height
        self._object_counter = solutions.ObjectCounter(
            show=show,
            region=[(600, 50), (600, 650)],
            model=self._model,
            classes=classes,
            # classes=[0], # person
            # classes=[4], # airplane
        )

    def count_objects(self, frame):
        return self._object_counter(frame)

    def predict_image(self, frame):
        return self._model.predict(frame, show=False, verbose=False)[0]

