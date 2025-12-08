from PyQt6.QtCore import QTimer

class CameraDetector:
    def __init__(self, camera_manager):
        self.camera_manager = camera_manager

    def detect_async(self, callback):
        QTimer.singleShot(10, lambda: callback(self.camera_manager.detect_cameras()))
