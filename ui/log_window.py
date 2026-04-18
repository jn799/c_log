import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QTextEdit, QSizePolicy, QPushButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QTextOption

from core.jsonl_parser import parse_session_messages


class _AutoTextEdit(QTextEdit):
    """Read-only QTextEdit that expands to its full document height."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setObjectName("MessageBodyEdit")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.document().contentsChanged.connect(self._fit)

    def _fit(self):
        vw = self.viewport().width()
        if vw > 0:
            self.document().setTextWidth(vw)
        h = max(20, int(self.document().size().height()) + 10)
        self.setFixedHeight(h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()

    def sizeHint(self):
        vw = self.viewport().width()
        if vw > 0:
            self.document().setTextWidth(vw)
        h = max(20, int(self.document().size().height()) + 10)
        return QSize(super().sizeHint().width(), h)


class _ToolBadge(QPushButton):
    """Checkable badge button that toggles its paired detail panel."""

    def __init__(self, name: str, detail: QFrame, parent=None):
        super().__init__(f"⚙ {name}", parent)
        self.setObjectName("ToolCallBadge")
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._detail = detail
        self.toggled.connect(detail.setVisible)


def _make_tool_detail(tc: dict) -> QFrame:
    detail = QFrame()
    detail.setObjectName("ToolDetail")
    detail.hide()
    lay = QVBoxLayout(detail)
    lay.setContentsMargins(8, 4, 8, 4)
    lay.setSpacing(0)

    inp = tc.get("input")
    if inp:
        text = json.dumps(inp, indent=2, ensure_ascii=False)
        edit = QTextEdit()
        edit.setObjectName("ToolDetailInput")
        edit.setReadOnly(True)
        edit.setPlainText(text)
        edit.setMaximumHeight(160)
        edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lay.addWidget(edit)
    else:
        lay.addWidget(QLabel("(no input)"))
    return detail


class MessageBubble(QFrame):
    def __init__(self, msg: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("MessageBubble")
        role = msg["role"]
        self.setProperty("role", role)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        # ── Header row ──
        header = QHBoxLayout()
        header.setSpacing(8)

        role_label = QLabel("USER" if role == "user" else "ASSISTANT")
        role_label.setObjectName("RoleLabel")
        role_label.setProperty("role", role)

        ts_label = QLabel(msg["timestamp"])
        ts_label.setObjectName("TimestampLabel")

        header.addWidget(role_label)

        if msg.get("thinking"):
            think_badge = QLabel("⏱ thinking")
            think_badge.setObjectName("ThinkingBadge")
            header.addWidget(think_badge)

        header.addWidget(ts_label)
        header.addStretch()

        if msg.get("output_tokens"):
            tok = QLabel(f"{msg['output_tokens']:,} tok")
            tok.setObjectName("MetaLabel")
            header.addWidget(tok)

        if msg.get("model"):
            mod = QLabel(msg["model"])
            mod.setObjectName("ModelChip")
            header.addWidget(mod)

        if msg.get("effort"):
            eff = QLabel(f"effort: {msg['effort']}")
            eff.setObjectName("EffortChip")
            header.addWidget(eff)

        layout.addLayout(header)

        sep = QFrame()
        sep.setObjectName("MsgSep")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # ── Tool calls — each badge toggles its own detail panel ──
        if msg.get("tool_calls"):
            tool_calls = msg["tool_calls"]
            tool_row = QHBoxLayout()
            tool_row.setSpacing(6)
            detail_panels = []

            for tc in tool_calls[:6]:
                detail = _make_tool_detail(tc)
                badge = _ToolBadge(tc["name"], detail)
                tool_row.addWidget(badge)
                detail_panels.append(detail)

            if len(tool_calls) > 6:
                more = QLabel(f"+{len(tool_calls)-6} more")
                more.setObjectName("SessionMeta")
                tool_row.addWidget(more)

            tool_row.addStretch()
            layout.addLayout(tool_row)
            for panel in detail_panels:
                layout.addWidget(panel)

        # ── Body ──
        text = msg.get("text", "")
        if text:
            body = _AutoTextEdit()
            if role == "assistant":
                body.setMarkdown(text)
            else:
                body.setPlainText(text)
            layout.addWidget(body)


class ToolExchangeSep(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ToolExchangeSep")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lbl = QLabel("↩ tool results")
        lbl.setObjectName("ToolExchangeLabel")
        lay.addWidget(lbl)
        lay.addStretch()


class LogWindow(QWidget):
    def __init__(self, session_meta: dict, parent=None):
        super().__init__(parent)
        title = session_meta.get("title", "Session")
        self.setWindowTitle(f"CLog — {title[:55]}")
        self.resize(900, 700)
        self.setObjectName("LogWindow")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──
        header = QWidget()
        header.setObjectName("LogHeader")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(16, 10, 16, 10)
        hlay.setSpacing(14)

        def chip(text, name):
            lbl = QLabel(text)
            lbl.setObjectName(name)
            return lbl

        hlay.addWidget(chip(session_meta.get("display_path", ""), "HeaderProject"))
        hlay.addWidget(chip("│", "HeaderSep"))
        hlay.addWidget(chip(session_meta.get("date", ""), "HeaderDate"))
        if session_meta.get("version"):
            hlay.addWidget(chip("│", "HeaderSep"))
            hlay.addWidget(chip(f"v{session_meta['version']}", "HeaderDate"))
        hlay.addStretch()
        hlay.addWidget(chip(session_meta.get("msg_count", ""), "HeaderMeta"))

        root.addWidget(header)

        div = QFrame()
        div.setObjectName("HeaderDivider")
        div.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(div)

        # ── Scroll area with messages ──
        scroll = QScrollArea()
        scroll.setObjectName("LogScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setObjectName("LogContainer")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(6)

        messages = parse_session_messages(session_meta["path"])
        for msg in messages:
            if msg["is_tool_exchange"]:
                vbox.addWidget(ToolExchangeSep())
            else:
                bubble = MessageBubble(msg)
                wrapper = QHBoxLayout()
                wrapper.setSpacing(0)
                wrapper.setContentsMargins(0, 0, 0, 0)
                if msg["role"] == "user":
                    wrapper.addStretch(1)
                    wrapper.addWidget(bubble, 4)
                else:
                    wrapper.addWidget(bubble, 4)
                    wrapper.addStretch(1)
                vbox.addLayout(wrapper)

        if not messages:
            empty = QLabel("No messages found.")
            empty.setObjectName("EmptyLabel")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(empty)

        vbox.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)
