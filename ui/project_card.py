from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QApplication,
    QToolButton, QMenu
)
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
    pin_changed = pyqtSignal(str, bool)   # (path, new_pinned_state)
    update_requested = pyqtSignal(str)    # path

    def __init__(self, name: str, session_count: int, path: str,
                 last_session_ts: str = "", pinned: bool = False, parent=None):
        super().__init__(parent)
        self.project_name = name
        self.project_path = path
        self.last_session_ts = last_session_ts
        self._session_count = session_count
        self._pinned = pinned
        self.setObjectName("ProjectCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("pinned", "true" if pinned else "false")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 4)
        outer.setSpacing(2)

        # ── Main row ──
        row = QHBoxLayout()
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(6)

        self._drag_handle = _DragHandle(self)
        self._drag_handle.setVisible(pinned)

        self._pin_icon = QLabel("⊛")
        self._pin_icon.setObjectName("PinIcon")
        self._pin_icon.setVisible(pinned)

        arrow = QLabel("▶")
        arrow.setObjectName("ProjectArrow")

        name_lbl = QLabel(name)
        name_lbl.setObjectName("ProjectName")

        self._count_lbl = QLabel(str(session_count))
        self._count_lbl.setObjectName("ProjectCount")

        self._menu_btn = QToolButton()
        self._menu_btn.setText("⋯")
        self._menu_btn.setObjectName("CardMenuBtn")
        self._menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._menu_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._menu = QMenu(self._menu_btn)
        self._menu.setObjectName("CardMenu")
        self._pin_action = self._menu.addAction("Unpin" if pinned else "Pin")
        self._pin_action.triggered.connect(self._toggle_pin)
        self._menu.addAction("Update").triggered.connect(
            lambda: self.update_requested.emit(self.project_path)
        )
        self._menu.addSeparator()
        self._menu.addAction("Remove").triggered.connect(
            lambda: self.remove_requested.emit(self.project_path)
        )
        self._menu_btn.setMenu(self._menu)

        row.addWidget(self._drag_handle)
        row.addWidget(self._pin_icon)
        row.addWidget(arrow)
        row.addWidget(name_lbl, 1)
        row.addWidget(self._count_lbl)
        row.addWidget(self._menu_btn)
        outer.addLayout(row)

        # ── Last session row ──
        self._last_lbl = QLabel(self._fmt_last(last_session_ts))
        self._last_lbl.setObjectName("ProjectLastAccessed")
        self._last_lbl.setContentsMargins(38, 0, 8, 0)
        self._last_lbl.setVisible(bool(last_session_ts))
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

    def update_last_session_ts(self, ts: str):
        self.last_session_ts = ts
        text = self._fmt_last(ts)
        self._last_lbl.setText(text)
        self._last_lbl.setVisible(bool(text))

    def set_pinned(self, pinned: bool):
        self._pinned = pinned
        self._drag_handle.setVisible(pinned)
        self._pin_icon.setVisible(pinned)
        self._pin_action.setText("Unpin" if pinned else "Pin")
        self.setProperty("pinned", "true" if pinned else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    # ── Toggle pin ────────────────────────────────────────────────────────────

    def _toggle_pin(self):
        new_pinned = not self._pinned
        self.set_pinned(new_pinned)
        self.pin_changed.emit(self.project_path, new_pinned)

    # ── Events ────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self._menu.exec(event.globalPosition().toPoint())
        elif event.button() == Qt.MouseButton.LeftButton:
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
