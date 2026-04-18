from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class ProjectCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, name: str, session_count: int, parent=None):
        super().__init__(parent)
        self.project_name = name
        self.setObjectName("ProjectCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(6)

        arrow = QLabel("▶")
        arrow.setObjectName("ProjectArrow")

        name_lbl = QLabel(name)
        name_lbl.setObjectName("ProjectName")

        count_lbl = QLabel(str(session_count))
        count_lbl.setObjectName("ProjectCount")

        layout.addWidget(arrow)
        layout.addWidget(name_lbl, 1)
        layout.addWidget(count_lbl)

    def set_active(self, active: bool):
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.project_name)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)

    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)
