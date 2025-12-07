from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt

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

        self.load_stylesheet()
        self.init_ui()


    def load_stylesheet(self):
        paths = [
            "styles/base.qss",
            "styles/combo.qss",
            "styles/button.qss",
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

        if self.camera_list:
            self.camera_combo.addItems(self.camera_list)
            self.camera_combo.setEnabled(True)
        else:
            self.camera_combo.addItem("인식된 카메라가 없습니다")
            self.camera_combo.setEnabled(False)

        self.camera_combo.setMinimumWidth(250)

        self.run_button = QPushButton("켜기")
        self.run_button.setEnabled(False)

        self.minimize_btn = QPushButton("-")
        self.minimize_btn.setObjectName("minimizeButton")
        self.minimize_btn.setFixedWidth(40)
        self.minimize_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton("X")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedWidth(40)
        self.close_btn.clicked.connect(self.close)

        top_layout.addWidget(self.camera_label)
        top_layout.addWidget(self.camera_combo)
        top_layout.addWidget(self.run_button)

        top_layout.addStretch()

        top_layout.addWidget(self.minimize_btn)
        top_layout.addWidget(self.close_btn)

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
        main_layout.addLayout(video_layout)
