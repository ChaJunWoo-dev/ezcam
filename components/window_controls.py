from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
import qtawesome as qta

class WindowControls(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(qta.icon("fa5s.minus", color="#2b2b2b"))
        self.minimize_btn.setObjectName("minimizeButton")
        self.minimize_btn.setFixedWidth(40)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(qta.icon("fa5s.times", color="white"))
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedWidth(40)

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.close_btn)

    def connect_signals(self, minimize_callback, close_callback):
        self.minimize_btn.clicked.connect(minimize_callback)
        self.close_btn.clicked.connect(close_callback)
