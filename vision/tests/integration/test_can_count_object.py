import time

from src.infrastructure.camera_adapter import CameraAdapter
from src.infrastructure.image_prediction_adapter import ImagePredictorAdapter


def test_can_count_object():
    camera_adapter = CameraAdapter()
    image_predictor = ImagePredictorAdapter("yolo26n.pt")
    frame = camera_adapter.read_image("one_person_image.jpg")

    object_count = image_predictor.count_objects(frame)

    assert object_count.total_tracks == 1
