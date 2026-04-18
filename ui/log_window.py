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


class ToolCallBadge(QLabel):
    def __init__(self, name: str, parent=None):
        super().__init__(f"  ⚙ {name}  ", parent)
        self.setObjectName("ToolCallBadge")


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

        layout.addLayout(header)

        sep = QFrame()
        sep.setObjectName("MsgSep")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # ── Tool calls ──
        if msg.get("tool_calls"):
            tool_row = QHBoxLayout()
            tool_row.setSpacing(6)
            for tc in msg["tool_calls"][:6]:
                tool_row.addWidget(ToolCallBadge(tc["name"]))
            if len(msg["tool_calls"]) > 6:
                tool_row.addWidget(QLabel(f"+{len(msg['tool_calls'])-6} more"))
            tool_row.addStretch()
            layout.addLayout(tool_row)

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
        self.setWindowTitle(f"Claude Log — {title[:55]}")
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
        hlay.addWidget(chip(session_meta.get("model", ""), "HeaderModel"))
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
                vbox.addWidget(MessageBubble(msg))

        if not messages:
            empty = QLabel("No messages found.")
            empty.setObjectName("EmptyLabel")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(empty)

        vbox.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)
