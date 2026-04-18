#!/usr/bin/env python3
import sys
import os

# Allow running from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QIcon
from ui.main_window import MainWindow
from ui.stylesheet import QSS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CLog")
    app.setOrganizationName("clog")

    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    app.setStyleSheet(QSS)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
