from PyQt6.QtCore import QThread, pyqtSignal

class CameraDetectWorekr(QThread):
    detected = pyqtSignal(list)

    def __init__(self, camera_manager):
        super().__init__()
        self.camera_manager = camera_manager

    def run(self):
        cameras = self.camera_manager.detect_cameras()
        self.detected.emit(cameras)

