from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent

from core import config


def _resolve_title(meta: dict) -> str:
    """Priority: user rename → custom-title from JSONL → first message."""
    cached = config.get_cached_title(meta["uuid"])
    if cached:
        return cached
    if meta.get("custom_title"):
        return meta["custom_title"]
    return meta.get("title", meta["uuid"][:8])


class _TitleEdit(QLineEdit):
    """Inline title editor — commits on Enter, cancels on Escape."""
    commit = pyqtSignal(str)
    cancel = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.commit.emit(self.text().strip())
        elif event.key() == Qt.Key.Key_Escape:
            self.cancel.emit()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.cancel.emit()
        super().focusOutEvent(event)


class SessionCard(QFrame):
    clicked = pyqtSignal(dict)   # emits full session metadata dict
    renamed = pyqtSignal(str)    # emits new title

    def __init__(self, session_meta: dict, parent=None):
        super().__init__(parent)
        self.session_meta = session_meta
        self._editing = False
        self.setObjectName("SessionCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        # ── Title row (label ↔ edit field via QStackedWidget) ──
        self._stack = QStackedWidget()
        self._stack.setFixedHeight(20)

        self._title_label = QLabel(_resolve_title(session_meta))
        self._title_label.setObjectName("SessionTitle")
        self._title_label.setWordWrap(False)

        self._title_edit = _TitleEdit()
        self._title_edit.setObjectName("SessionTitleEdit")
        self._title_edit.commit.connect(self._commit_rename)
        self._title_edit.cancel.connect(self._cancel_rename)

        self._stack.addWidget(self._title_label)   # index 0
        self._stack.addWidget(self._title_edit)    # index 1
        self._stack.setCurrentIndex(0)

        layout.addWidget(self._stack)

        # ── Meta row ──
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        date_lbl = QLabel(session_meta.get("date", ""))
        date_lbl.setObjectName("SessionMeta")

        dot = QLabel("·")
        dot.setObjectName("SessionMeta")

        count_lbl = QLabel(session_meta.get("msg_count", ""))
        count_lbl.setObjectName("SessionMeta")

        hint = QLabel("double-click to rename")
        hint.setObjectName("RenameHint")

        meta_row.addWidget(date_lbl)
        meta_row.addWidget(dot)
        meta_row.addWidget(count_lbl)
        meta_row.addStretch()
        meta_row.addWidget(hint)

        model = session_meta.get("model", "")
        if model:
            model_lbl = QLabel(model)
            model_lbl.setObjectName("SessionModel")
            meta_row.addWidget(model_lbl)

        layout.addLayout(meta_row)

    # ── Rename logic ──────────────────────────────────────────────────────────

    def _start_rename(self):
        self._editing = True
        self._title_edit.setText(self._title_label.text())
        self._stack.setCurrentIndex(1)
        self._title_edit.selectAll()
        self._title_edit.setFocus()

    def _commit_rename(self, new_title: str):
        if new_title:
            config.cache_title(self.session_meta["uuid"], new_title)
            self._title_label.setText(new_title)
            self.renamed.emit(new_title)
        self._cancel_rename()

    def _cancel_rename(self):
        self._editing = False
        self._stack.setCurrentIndex(0)

    # ── Events ───────────────────────────────────────────────────────────────

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_rename()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._editing:
            self.clicked.emit(self.session_meta)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)

    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)
