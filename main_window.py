from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QSlider, QLineEdit
)
from PyQt6.QtCore import Qt
import qtawesome as qta

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
        self.camera_list = []
        self.is_running = False

        self.load_stylesheet()
        self.init_ui()

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
        top_layout = QHBoxLayout()

        self.camera_label = QLabel("카메라: ")
        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumWidth(250)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#2b2b2b'))
        self.refresh_btn.setFixedWidth(40)

        self.run_button = QPushButton("켜기")
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.toggle_camera)

        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(qta.icon('fa5s.minus', color='#2b2b2b'))
        self.minimize_btn.setObjectName("minimizeButton")
        self.minimize_btn.setFixedWidth(40)
        self.minimize_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(qta.icon('fa5s.times', color='white'))
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedWidth(40)
        self.close_btn.clicked.connect(self.close)

        top_layout.addWidget(self.camera_label)
        top_layout.addWidget(self.camera_combo)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.run_button)

        top_layout.addStretch()

        top_layout.addWidget(self.minimize_btn)
        top_layout.addWidget(self.close_btn)

        # 슬라이더
        self.sense_label = QLabel("배경 감도:")
        self.sense_slider = QSlider(Qt.Orientation.Horizontal)
        self.sense_slider.setMinimum(1)
        self.sense_slider.setMaximum(10)
        self.sense_slider.setValue(7)
        self.sense_slider.valueChanged.connect(self.slider_changed)

        self.sense_input = QLineEdit("0.7")
        self.sense_input.setFixedWidth(50)
        self.sense_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sense_input.textChanged.connect(self.input_changed)

        slider_layout = QHBoxLayout()

        slider_layout.addWidget(self.sense_label)
        slider_layout.addWidget(self.sense_slider)
        slider_layout.addWidget(self.sense_input)
        slider_layout.addStretch()

        # 캠 영역
        video_layout = QHBoxLayout()

        self.original_area = QLabel("원본 캠")
        self.original_area.setMinimumSize(640, 480)
        self.original_area.setObjectName("originalVideo")

        self.removed_bg_area = QLabel("배경 제거")
        self.removed_bg_area.setObjectName("removedBgArea")
        self.removed_bg_area.setMinimumSize(640, 480)

        video_layout.addWidget(self.original_area)
        video_layout.addWidget(self.removed_bg_area)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(12)
        main_layout.addLayout(slider_layout)
        main_layout.addLayout(video_layout)

    def slider_changed(self, value):
        self.sense_input.setText(f"{value / 10:.1f}")

    def input_changed(self):
        try:
            value = float(self.sense_input.text())
            if 0.1 <= value <= 1.0:
                self.sense_slider.blockSignals(True)
                self.sense_slider.setValue(int(value * 10))
                self.sense_slider.blockSignals(False)
        except ValueError:
            pass

    def toggle_camera(self):
        if self.is_running:
            self.is_running = False
        else:
            self.is_running = True
