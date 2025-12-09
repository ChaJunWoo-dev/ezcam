from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2

from camera_manager import CameraManager
from components import CameraDetector, WindowControls, CameraSelector, Slider, CameraView
from background_remover import remove_bg, apply_green_bg
from overlay_window import OverlayWindow
from mouse_event import MouseEvent

class MainApp(QMainWindow, MouseEvent):
    def __init__(self):
        super().__init__()
        MouseEvent.__init__(self)

        self.setWindowTitle("EZCAM - AI 캠 배경 제거")
        self.setGeometry(100, 100, 1400, 600)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

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
        central.setMouseTracking(True)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()

        self.camera_selector = CameraSelector()
        self.camera_selector.connect_refresh(self.redetect_cameras)

        self.run_button = QPushButton("켜기")
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.toggle_camera)

        self.overlay_button = QPushButton("오버레이")
        self.overlay_button.setEnabled(False)
        self.overlay_button.clicked.connect(self.start_overlay_mode)

        self.window_controls = WindowControls()
        self.window_controls.connect_signals(self.showMinimized, self.close)

        top_layout.addWidget(self.camera_selector)
        top_layout.addWidget(self.run_button)
        top_layout.addWidget(self.overlay_button)
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

        # 모든 자식 위젯에 마우스 트래킹 활성화
        for widget in self.findChildren(QWidget):
            widget.setMouseTracking(True)

    def find_cameras(self):
        self.camera_selector.set_loading_state()
        self.run_button.setEnabled(False)
        self.camera_detector.detect_async(self._on_cameras_detected)

    def redetect_cameras(self):
        self.stop_camera()
        self.find_cameras()

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
            self.overlay_button.setEnabled(True)

    def stop_camera(self):
        self.camera_manager.on_stop_camera()
        self.timer.stop()
        self.original_area.clear()
        self.removed_bg_area.clear()
        self.run_button.setText("켜기")
        self.overlay_button.setEnabled(False)

    def update_frame(self):
        frame = self.camera_manager.get_frame()

        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.show_original(rgb)

        clean_bg = remove_bg(frame)
        processed_bg = apply_green_bg(clean_bg)
        self.show_chroma(processed_bg)

    def show_original(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(q_img)
        self.original_area.update_frame(pix)

    def show_chroma(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        rgba = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA)
        q_img = QImage(rgba.data, w, h, bytes_per_line, QImage.Format.Format_RGBA8888)
        pix = QPixmap.fromImage(q_img)
        self.removed_bg_area.update_frame(pix)

    def start_overlay_mode(self):
        self.overlay_window = OverlayWindow(self, self.camera_manager)
        self.overlay_window.show()
        self.hide()
