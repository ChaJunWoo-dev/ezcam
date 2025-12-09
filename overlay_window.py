from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

from mouse_event import MouseEvent
from background_remover import remove_bg

class OverlayWindow(QLabel, MouseEvent):
    def __init__(self, main_app, camera_manager):
        super().__init__()
        MouseEvent.__init__(self)
        self.main_app = main_app
        self.camera_manager = camera_manager

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(640, 480)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)

    def update_frame(self):
        frame = self.camera_manager.get_frame()

        if frame is None:
            return

        clean_bg = remove_bg(frame)
        h, w, ch = clean_bg.shape
        bytes_per_line = ch * w
        qimg = QImage(clean_bg.data, w, h, bytes_per_line, QImage.Format.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg).scaled(self.size())
        self.setPixmap(pix)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.main_app.show()

    def resize_overlay(self, width, height):
        self.resize(width, height)

        if self.pixmap():
            scaled_pix = self.pixmap().scaled(
                self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio
            )
            self.setPixmap(scaled_pix)
