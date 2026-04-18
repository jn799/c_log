from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag

from core.jsonl_parser import _fmt_ts


class _DragHandle(QLabel):
    def __init__(self, card, parent=None):
        super().__init__("⠿", parent)
        self.setObjectName("DragHandle")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._card = card
        self._start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pos = event.pos()
        event.accept()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self._start_pos is None:
            return
        if (event.pos() - self._start_pos).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self._card)
        mime = QMimeData()
        mime.setData("application/x-clog-project", self._card.project_path.encode())
        drag.setMimeData(mime)
        drag.setPixmap(self._card.grab())
        drag.setHotSpot(self._card.mapFromGlobal(self.mapToGlobal(self._start_pos)))
        self._start_pos = None
        drag.exec(Qt.DropAction.MoveAction)

    def mouseReleaseEvent(self, event):
        self._start_pos = None
        event.accept()


class ProjectCard(QFrame):
    clicked = pyqtSignal(str)
    remove_requested = pyqtSignal(str)

    def __init__(self, name: str, session_count: int, path: str,
                 last_accessed: str = "", parent=None):
        super().__init__(parent)
        self.project_name = name
        self.project_path = path
        self._session_count = session_count
        self.setObjectName("ProjectCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 4)
        outer.setSpacing(2)

        # ── Main row ──
        row = QHBoxLayout()
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(6)

        self._drag_handle = _DragHandle(self)
        arrow = QLabel("▶")
        arrow.setObjectName("ProjectArrow")

        name_lbl = QLabel(name)
        name_lbl.setObjectName("ProjectName")

        self._count_lbl = QLabel(str(session_count))
        self._count_lbl.setObjectName("ProjectCount")

        trash_btn = QPushButton("🗑")
        trash_btn.setObjectName("TrashBtn")
        trash_btn.setFixedSize(22, 22)
        trash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        trash_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        trash_btn.setToolTip("Remove project from view")
        trash_btn.clicked.connect(lambda: self.remove_requested.emit(self.project_path))

        row.addWidget(self._drag_handle)
        row.addWidget(arrow)
        row.addWidget(name_lbl, 1)
        row.addWidget(self._count_lbl)
        row.addWidget(trash_btn)
        outer.addLayout(row)

        # ── Last-accessed row ──
        self._last_lbl = QLabel(self._fmt_last(last_accessed))
        self._last_lbl.setObjectName("ProjectLastAccessed")
        self._last_lbl.setContentsMargins(38, 0, 8, 0)   # indent to align under name
        if not last_accessed:
            self._last_lbl.hide()
        outer.addWidget(self._last_lbl)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _fmt_last(ts: str) -> str:
        if not ts:
            return ""
        result = _fmt_ts(ts)
        return f"Last: {result}" if result else ""

    # ── Public API ────────────────────────────────────────────────────────────

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        for child in self.findChildren(QLabel):
            child.style().unpolish(child)
            child.style().polish(child)
        self.update()

    def update_count(self, session_count: int):
        self._session_count = session_count
        self._count_lbl.setText(str(session_count))

    def update_last_accessed(self, ts: str):
        text = self._fmt_last(ts)
        self._last_lbl.setText(text)
        self._last_lbl.setVisible(bool(text))

    # ── Events ────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.project_path)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setProperty("hovered", "true")
        self.style().unpolish(self)
        self.style().polish(self)

    def leaveEvent(self, event):
        self.setProperty("hovered", "false")
        self.style().unpolish(self)
        self.style().polish(self)
