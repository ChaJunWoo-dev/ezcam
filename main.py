import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainApp

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
