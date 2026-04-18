from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class SessionCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, session_data: dict, parent=None):
        super().__init__(parent)
        self.session_data = session_data
        self.setObjectName("SessionCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        title = QLabel(session_data["title"])
        title.setObjectName("SessionTitle")
        title.setWordWrap(False)
        title.setMaximumWidth(480)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)

        date_lbl = QLabel(session_data["date"])
        date_lbl.setObjectName("SessionMeta")

        count_lbl = QLabel(session_data["msg_count"])
        count_lbl.setObjectName("SessionMeta")

        model_lbl = QLabel(session_data["model"])
        model_lbl.setObjectName("SessionModel")

        meta_row.addWidget(date_lbl)
        meta_row.addWidget(QLabel("·"))
        meta_row.addWidget(count_lbl)
        meta_row.addStretch()
        meta_row.addWidget(model_lbl)

        layout.addWidget(title)
        layout.addLayout(meta_row)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.session_data)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)

    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)
