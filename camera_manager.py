import cv2
from pygrabber.dshow_graph import FilterGraph

class CameraManager:
    def __init__(self):
        self.is_running = False

    def detect_cameras(self):
        available_cameras = []
        graph = FilterGraph()
        device_names = graph.get_input_devices()
        max_cameras = min(len(device_names) + 1, 3)

        for i in range(max_cameras):
            capture = cv2.VideoCapture(i)

            if capture.isOpened():
                ret, _ = capture.read()

                if ret:
                    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    device_name = device_names[i] if i < len(device_names) else f"카메라 {i}"

                    camera_info = {
                        'index': i,
                        'name': device_name,
                        'size': f"{width}x{height}"
                    }

                    available_cameras.append(camera_info)

            capture.release()

        return available_cameras
