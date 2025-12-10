from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2

from core.camera_manager import cam_manager
from components import WindowControls, CameraSelector, Slider, CameraView
from core.background_remover import bg_remover
from windows.overlay_window import OverlayWindow
from core.mouse_event import MouseEvent
from workers import ModelLoadWorker, CameraDetectWorekr

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

        self.is_cam_ready = False
        self.is_model_ready = False

        self.model_loader = ModelLoadWorker(bg_remover)
        self.model_loader.loaded.connect(self._on_model_loaded)
        self.model_loader.start()

        self.camera_detector = CameraDetectWorekr(cam_manager)
        self.camera_detector.detected.connect(self._on_cameras_detected)
        self.camera_detector.start()

        self.load_stylesheet()
        self.init_ui()
        self.camera_selector.set_loading_state()

    def load_stylesheet(self):
        paths = [
            "styles/base.qss",
            "styles/combo.qss",
            "styles/button.qss",
            "styles/slider.qss",
        ]

        qss = ""

        for path in paths:
            with open(path, "r", encoding="utf-8") as f:
                qss += f.read()

        self.setStyleSheet(qss)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        central.setMouseTracking(True)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)

        top_layout = QHBoxLayout()

        self.camera_selector = CameraSelector()
        self.camera_selector.connect_refresh(self.redetect_cameras)

        self.model_status_label = QLabel("배경 제거 준비 중...")
        self.model_status_label.setStyleSheet("color: #888; font-size: 12px;")

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
        top_layout.addWidget(self.model_status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.window_controls)

        self.slider = Slider(label_text="배경 감도:", initial_value=0.7)
        self.slider.value_changed.connect(self._on_threshold_changed)

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

        for widget in self.findChildren(QWidget):
            widget.setMouseTracking(True)

    def redetect_cameras(self):
        if cam_manager.is_running:
            self.stop_camera()
        self.is_cam_ready = False
        self.run_button.setEnabled(False)
        self.camera_selector.set_loading_state()

        self.redetect_worker = CameraDetectWorekr(cam_manager)
        self.redetect_worker.detected.connect(self._on_cameras_detected)
        self.redetect_worker.start()

    def toggle_camera(self):
        if cam_manager.is_running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        camera = self.camera_selector.get_selected_camera()

        if camera:
            cam_manager.on_start_camera(camera["index"])
            self.timer.start(33)
            self.run_button.setText("끄기")
            self.overlay_button.setEnabled(True)

    def stop_camera(self):
        cam_manager.on_stop_camera()
        self.timer.stop()
        self.original_area.clear()
        self.removed_bg_area.clear()
        self.run_button.setText("켜기")
        self.overlay_button.setEnabled(False)

    def start_overlay_mode(self):
        self.overlay_window = OverlayWindow(self, cam_manager)
        self.overlay_window.show()
        self.hide()

    def update_frame(self):
        frame = cam_manager.get_frame()

        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.show_original(rgb)

        clean_bg = bg_remover.remove_bg(frame)
        processed_bg = bg_remover.apply_green_bg(clean_bg)
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

    def _check_ready(self):
        if self.is_model_ready and self.is_cam_ready:
            self.run_button.setEnabled(True)

    def _on_model_loaded(self):
        self.is_model_ready = True
        self.model_status_label.hide()
        self._check_ready()

    def _on_cameras_detected(self, cameras):
        self.camera_selector.update_cameras(cameras)
        self.is_cam_ready = len(cameras) > 0
        self._check_ready()

    def _on_threshold_changed(self, value):
        bg_remover.set_threshold(value)

    def closeEvent(self, event):
        if self.camera_detector.isRunning():
            self.camera_detector.wait()
        if self.model_loader.isRunning():
            self.model_loader.wait()
        if hasattr(self, 'redetect_worker') and self.redetect_worker.isRunning():
            self.redetect_worker.wait()
        event.accept()
