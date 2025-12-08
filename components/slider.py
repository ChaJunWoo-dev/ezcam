from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal

class Slider(QWidget):
    value_changed = pyqtSignal(float)

    def __init__(self, label_text="", initial_value=0.5):
        super().__init__()
        self.label_text = label_text
        self.initial_value = initial_value
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self.label_text)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)
        self.slider.setValue(int(self.initial_value * 10))
        self.slider.valueChanged.connect(self._slider_changed)

        self.input = QLineEdit(f"{self.initial_value:.1f}")
        self.input.setFixedWidth(50)
        self.input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input.textChanged.connect(self._input_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.input)

    def _slider_changed(self, value):
        float_value = value / 10.0
        self.input.setText(f"{float_value:.1f}")
        self.value_changed.emit(float_value)

    def _input_changed(self):
        try:
            value = float(self.input.text())
            if 0.1 <= value <= 1.0:
                self.slider.blockSignals(True)
                self.slider.setValue(int(value * 10))
                self.slider.blockSignals(False)
                self.value_changed.emit(value)
        except ValueError:
            pass

    def get_value(self):
        return self.slider.value() / 10.0

    def set_value(self, value):
        if 0.1 <= value <= 1.0:
            self.slider.setValue(int(value * 10))
