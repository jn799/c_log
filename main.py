#!/usr/bin/env python3
import sys
import os

# Allow running from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from ui.main_window import MainWindow
from ui.stylesheet import QSS

_SOCKET_NAME = "claude_log_instance"


def _raise_window(window: MainWindow):
    window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized)
    window.show()
    window.raise_()
    window.activateWindow()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("claude_log")
    app.setOrganizationName("clog")
    app.setDesktopFileName("claude_log")  # GNOME Wayland: links windows to claude_log.desktop

    # Single-instance check: try to contact an already-running instance
    probe = QLocalSocket()
    probe.connectToServer(_SOCKET_NAME)
    if probe.waitForConnected(300):
        probe.write(b"raise")
        probe.flush()
        probe.waitForBytesWritten(300)
        probe.close()
        sys.exit(0)
    probe.close()

    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    app.setStyleSheet(QSS)

    window = MainWindow()
    window.show()

    # Start the single-instance server so subsequent launches hit us
    server = QLocalServer()
    QLocalServer.removeServer(_SOCKET_NAME)  # clear any stale socket from a crash
    server.listen(_SOCKET_NAME)

    def _on_new_connection():
        conn = server.nextPendingConnection()
        if conn:
            conn.waitForReadyRead(200)
            conn.close()
            _raise_window(window)

    server.newConnection.connect(_on_new_connection)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
