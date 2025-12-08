from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

class CameraView(QLabel):
    def __init__(self, title="카메라"):
        super().__init__()
        self.title = title
        self.setText(title)
        self.setMinimumSize(640, 480)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_frame(self, pixmap):
        self.setPixmap(pixmap)

    def clear(self):
        super().clear()
        self.setText(self.title)
