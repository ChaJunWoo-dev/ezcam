from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

from camera_manager import CameraManager
from components import CameraDetector, WindowControls, CameraSelector, Slider, CameraView
import cv2

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("EZCAM - AI 캠 배경 제거")
        self.setGeometry(100, 100, 1400, 600)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.drag_pos = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.camera_manager = CameraManager()
        self.camera_detector = CameraDetector(self.camera_manager)

        self.load_stylesheet()
        self.init_ui()
        self.find_cameras()

    def load_stylesheet(self):
        paths = [
            "styles/base.qss",
            "styles/combo.qss",
            "styles/button.qss",
            "styles/slider.qss",
        ]

        try:
            qss = ""

            for path in paths:
                with open(path, "r", encoding="utf-8") as f:
                    qss += f.read()

            self.setStyleSheet(qss)
        except Exception as e:
            print("QSS 파일 로딩 실패:", e)


    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()

        self.camera_selector = CameraSelector()
        self.camera_selector.connect_refresh(self.find_cameras)

        self.run_button = QPushButton("켜기")
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.toggle_camera)

        self.window_controls = WindowControls()
        self.window_controls.connect_signals(self.showMinimized, self.close)

        top_layout.addWidget(self.camera_selector)
        top_layout.addWidget(self.run_button)
        top_layout.addStretch()
        top_layout.addWidget(self.window_controls)

        self.slider = Slider(label_text="배경 감도:", initial_value=0.7)

        video_layout = QHBoxLayout()

        self.original_area = CameraView("원본 캠")
        self.original_area.setObjectName("originalVideo")

        self.removed_bg_area = CameraView("배경 제거")
        self.removed_bg_area.setObjectName("removedBgArea")

        video_layout.addWidget(self.original_area)
        video_layout.addWidget(self.removed_bg_area)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(12)
        main_layout.addWidget(self.slider)
        main_layout.addLayout(video_layout)

    def find_cameras(self):
        self.camera_selector.set_loading_state()
        self.run_button.setEnabled(False)
        self.camera_detector.detect_async(self._on_cameras_detected)

    def _on_cameras_detected(self, cameras):
        self.camera_selector.update_cameras(cameras)
        if cameras:
            self.run_button.setEnabled(True)

    def toggle_camera(self):
        if self.camera_manager.is_running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        camera = self.camera_selector.get_selected_camera()

        if camera:
            self.camera_manager.on_start_camera(camera["index"])
            self.timer.start(33)
            self.run_button.setText("끄기")

    def stop_camera(self):
        pass

    def update_frame(self):
        frame = self.camera_manager.get_frame()

        if frame is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_frame.shape
            bytes_per_line = channel * width
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.original_area.update_frame(pixmap)

