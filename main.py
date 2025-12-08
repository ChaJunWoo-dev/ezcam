import sys
import os

# OpenCV 에러 메시지 억제 (반드시 cv2 import 전에 설정)
os.environ['OPENCV_LOG_LEVEL'] = 'FATAL'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'

from PyQt6.QtWidgets import QApplication
from main_window import MainApp

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
