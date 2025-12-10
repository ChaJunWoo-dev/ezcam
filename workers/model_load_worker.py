from PyQt6.QtCore import QThread, pyqtSignal

class ModelLoadWorker(QThread):
    loaded = pyqtSignal()

    def __init__(self, bg_remover):
        super().__init__()
        self.bg_remover = bg_remover

    def run(self):
        self.bg_remover.model_lazy_load()
        self.loaded.emit()

