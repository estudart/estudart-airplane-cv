from dataclasses import dataclass

from ultralytics import YOLO, solutions



@dataclass
class CountedObject:
    detected_object: str
    confidence: float

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

    def count_objects(self, frame) -> (solutions.solutions.SolutionResults, CountedObject):
        previous_ids = set(self._object_counter.counted_ids)

        result = self._object_counter(frame)

        new_ids = self._object_counter.counted_ids - previous_ids

        counted_objects = [
            CountedObject(
                detected_object=self._object_counter.names[int(class_id)],
                confidence=float(confidence),
            )
            for track_id, class_id, confidence in zip(
                self._object_counter.track_ids,
                self._object_counter.clss,
                self._object_counter.confs,
            )
            if int(track_id) in new_ids
        ]

        return result, counted_objects

    def predict_image(self, frame):
        return self._model.predict(frame, show=False, verbose=False)[0]

