from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt


class ReportDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setObjectName("ReportDialog")
        self.setMinimumWidth(380)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(14)

        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("ReportMessage")
        msg_lbl.setWordWrap(True)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        lay.addWidget(msg_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("OkButton")
        ok_btn.setFixedSize(80, 28)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        lay.addLayout(btn_row)

    @staticmethod
    def show(title: str, message: str, parent=None):
        dlg = ReportDialog(title, message, parent)
        dlg.exec()
