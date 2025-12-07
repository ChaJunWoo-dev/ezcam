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
        try:
            with open("./resources/style.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("QSS 파일 로딩 실패:", e)


    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main = QVBoxLayout(central)
        top = QHBoxLayout()

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

        top.addWidget(self.camera_label)
        top.addWidget(self.camera_combo)
        top.addWidget(self.run_button)
        top.addStretch()

        main.addLayout(top)
