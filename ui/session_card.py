from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QStackedWidget, QToolButton, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent

from core import config, jsonl_parser
from ui.report_dialog import ReportDialog


def _resolve_title(meta: dict) -> str:
    cached = config.get_cached_title(meta["uuid"])
    if cached:
        return cached
    if meta.get("custom_title"):
        return meta["custom_title"]
    return meta.get("title", meta["uuid"][:8])


class _TitleEdit(QLineEdit):
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
    clicked = pyqtSignal(dict)
    renamed = pyqtSignal(str)
    updated = pyqtSignal(dict)
    pin_changed = pyqtSignal()

    def __init__(self, session_meta: dict, parent=None):
        super().__init__(parent)
        self.session_meta = dict(session_meta)
        self._editing = False
        self._pinned = config.is_pinned(session_meta["uuid"])
        self.setObjectName("SessionCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(68)
        self.setProperty("pinned", "true" if self._pinned else "false")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        # ── Title row: pin icon + stacked label/edit + 3-dot menu ──
        title_row = QHBoxLayout()
        title_row.setSpacing(6)

        self._pin_icon = QLabel("⊛")
        self._pin_icon.setObjectName("PinIcon")
        self._pin_icon.setVisible(self._pinned)
        title_row.addWidget(self._pin_icon)

        self._stack = QStackedWidget()
        self._stack.setFixedHeight(20)

        self._title_label = QLabel(_resolve_title(session_meta))
        self._title_label.setObjectName("SessionTitle")
        self._title_label.setWordWrap(False)

        self._title_edit = _TitleEdit()
        self._title_edit.setObjectName("SessionTitleEdit")
        self._title_edit.commit.connect(self._commit_rename)
        self._title_edit.cancel.connect(self._cancel_rename)

        self._stack.addWidget(self._title_label)
        self._stack.addWidget(self._title_edit)
        self._stack.setCurrentIndex(0)
        title_row.addWidget(self._stack, 1)

        self._menu_btn = QToolButton()
        self._menu_btn.setText("⋯")
        self._menu_btn.setObjectName("CardMenuBtn")
        self._menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._menu_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._menu = QMenu(self._menu_btn)
        self._menu.setObjectName("CardMenu")
        self._menu.addAction("Rename").triggered.connect(self._start_rename)
        self._menu.addAction("Update").triggered.connect(self._do_update)
        self._pin_action = self._menu.addAction("Unpin" if self._pinned else "Pin")
        self._pin_action.triggered.connect(self._toggle_pin)
        self._menu_btn.setMenu(self._menu)
        title_row.addWidget(self._menu_btn)

        layout.addLayout(title_row)

        # ── Meta row ──
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        self._date_lbl = QLabel(session_meta.get("date", ""))
        self._date_lbl.setObjectName("SessionMeta")
        self._count_lbl = QLabel(session_meta.get("msg_count", ""))
        self._count_lbl.setObjectName("SessionMeta")
        self._tok_dot = QLabel("·")
        self._tok_dot.setObjectName("SessionMeta")
        self._tok_lbl = QLabel(session_meta.get("total_tokens_fmt", ""))
        self._tok_lbl.setObjectName("SessionMeta")

        dot = QLabel("·")
        dot.setObjectName("SessionMeta")

        meta_row.addWidget(self._date_lbl)
        meta_row.addWidget(dot)
        meta_row.addWidget(self._count_lbl)
        meta_row.addWidget(self._tok_dot)
        meta_row.addWidget(self._tok_lbl)
        meta_row.addStretch()

        if not session_meta.get("total_tokens_fmt"):
            self._tok_dot.hide()
            self._tok_lbl.hide()

        layout.addLayout(meta_row)

    # ── Rename ────────────────────────────────────────────────────────────────

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

    # ── Update ────────────────────────────────────────────────────────────────

    def _do_update(self):
        new_meta = jsonl_parser.parse_session_metadata(self.session_meta["path"])
        if new_meta is None:
            QMessageBox.warning(self, "Update", "Could not read session file.")
            return

        old_tokens = self.session_meta.get("total_tokens", 0)
        old_count = self.session_meta.get("msg_count", "")
        new_tokens = new_meta.get("total_tokens", 0)
        new_count = new_meta.get("msg_count", "")

        if old_tokens == new_tokens and old_count == new_count:
            ReportDialog.show("Session Update", "This session is already up-to-date!", self)
            return

        self.session_meta = new_meta
        self._count_lbl.setText(new_count)
        tok_fmt = new_meta.get("total_tokens_fmt", "")
        self._tok_lbl.setText(tok_fmt)
        if tok_fmt:
            self._tok_dot.show()
            self._tok_lbl.show()
        else:
            self._tok_dot.hide()
            self._tok_lbl.hide()

        changes = []
        if old_count != new_count:
            changes.append(f"Messages:  {old_count}  →  {new_count}")
        if old_tokens != new_tokens:
            old_fmt = jsonl_parser._fmt_tokens(old_tokens) if old_tokens else "0"
            new_fmt = new_meta.get("total_tokens_fmt") or "0"
            changes.append(f"Tokens:  {old_fmt}  →  {new_fmt}")
        ReportDialog.show("Session Update", "Updated:\n\n• " + "\n• ".join(changes), self)
        self.updated.emit(new_meta)

    # ── Pin ───────────────────────────────────────────────────────────────────

    def _toggle_pin(self):
        uuid = self.session_meta["uuid"]
        if self._pinned:
            config.unpin_session(uuid)
            self._pinned = False
        else:
            config.pin_session(uuid)
            self._pinned = True
        self._pin_icon.setVisible(self._pinned)
        self._pin_action.setText("Unpin" if self._pinned else "Pin")
        self.setProperty("pinned", "true" if self._pinned else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.pin_changed.emit()

    # ── Events ────────────────────────────────────────────────────────────────

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
