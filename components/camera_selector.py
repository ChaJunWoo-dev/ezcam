from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton
import qtawesome as qta

class CameraSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.camera_list = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.camera_label = QLabel("카메라: ")

        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumWidth(250)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(qta.icon("fa5s.sync-alt", color="#2b2b2b"))
        self.refresh_btn.setFixedWidth(40)

        layout.addWidget(self.camera_label)
        layout.addWidget(self.camera_combo)
        layout.addWidget(self.refresh_btn)

    def set_loading_state(self):
        self.refresh_btn.setEnabled(False)
        self.camera_combo.clear()
        self.camera_combo.addItem("카메라 탐지 중...")

    def update_cameras(self, cameras):
        self.camera_list = cameras
        self.camera_combo.clear()

        if cameras:
            for camera in cameras:
                self.camera_combo.addItem(f"{camera['name']}")
        else:
            self.camera_combo.addItem("카메라를 찾을 수 없습니다")

        self.refresh_btn.setEnabled(True)

    def get_selected_camera(self):
        index = self.camera_combo.currentIndex()

        if 0 <= index < len(self.camera_list):
            return self.camera_list[index]

        return None

    def connect_refresh(self, callback):
        self.refresh_btn.clicked.connect(callback)
