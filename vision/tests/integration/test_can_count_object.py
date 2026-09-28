import time

from src.infrastructure.camera_adapter import CameraAdapter
from src.infrastructure.image_prediction_adapter import ImagePredictorAdapter


def test_can_count_object():
    camera_adapter = CameraAdapter("airplane-right-to-left-fixed-camera.mp4")
    video_writer = camera_adapter.get_writer("object_counting_output.avi")
    image_predictor = ImagePredictorAdapter("yolo26n.pt")
    
    while camera_adapter._cap.isOpened():
        success, im0 = camera_adapter._cap.read()

        if not success:
            break

        results = image_predictor._object_counter(im0)
        video_writer.write(results.plot_im)

    camera_adapter.close()
    video_writer.release()
    camera_adapter.close_all_windows()

    airplane_in = image_predictor._object_counter.classwise_count["airplane"]["IN"]
    airplane_out = image_predictor._object_counter.classwise_count["airplane"]["OUT"]

    assert airplane_out == 3
