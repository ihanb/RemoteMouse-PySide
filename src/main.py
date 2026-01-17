"""应用程序入口点"""

import sys
from PySide6.QtWidgets import QApplication
from gui_main_window import CameraApp


def main():
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()