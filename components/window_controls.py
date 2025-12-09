from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
import qtawesome as qta

class WindowControls(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.help_btn = QPushButton()
        self.help_btn.setIcon(qta.icon("fa5s.question-circle", color="#2b2b2b"))
        self.help_btn.setObjectName("helpButton")
        self.help_btn.setFixedWidth(40)
        self.help_btn.setToolTip(
            "단축키:\n"
            "• Ctrl + 마우스 드래그: 창 크기 조정\n"
            "• ESC: 오버레이 모드 종료"
        )
        self.help_btn.setToolTipDuration(0)

        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(qta.icon("fa5s.minus", color="#2b2b2b"))
        self.minimize_btn.setObjectName("minimizeButton")
        self.minimize_btn.setFixedWidth(40)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(qta.icon("fa5s.times", color="#2b2b2b"))
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedWidth(40)

        layout.addWidget(self.help_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.close_btn)

    def connect_signals(self, minimize_callback, close_callback):
        self.minimize_btn.clicked.connect(minimize_callback)
        self.close_btn.clicked.connect(close_callback)
