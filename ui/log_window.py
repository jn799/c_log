from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, "
    "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n\n"
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu "
    "fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
    "culpa qui officia deserunt mollit anim id est laborum."
)

DUMMY_MESSAGES = [
    ("user",      "2026-04-15 14:23:01", None,       None,  "Fix the authentication bug in the payment flow. When users try to checkout with a saved card, the JWT token expires mid-flow and they get a 401."),
    ("assistant", "2026-04-15 14:23:18", 1842, 12.4, LOREM),
    ("user",      "2026-04-15 14:25:03", None,       None,  "Can you also add a token refresh interceptor to the axios client?"),
    ("assistant", "2026-04-15 14:25:31", 2109, 18.7, LOREM + "\n\n" + LOREM),
    ("user",      "2026-04-15 14:28:45", None,       None,  "Looks good. Let's also write a test for the refresh logic."),
    ("assistant", "2026-04-15 14:29:02", 987,   8.1, LOREM),
]


class MessageBubble(QFrame):
    def __init__(self, role, timestamp, tokens, thinking_s, content, parent=None):
        super().__init__(parent)
        self.setObjectName("MessageBubble")
        self.setProperty("role", role)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(10)

        role_label = QLabel("USER" if role == "user" else "ASSISTANT")
        role_label.setObjectName("RoleLabel")
        role_label.setProperty("role", role)

        ts_label = QLabel(timestamp)
        ts_label.setObjectName("TimestampLabel")

        header.addWidget(role_label)
        header.addWidget(ts_label)
        header.addStretch()

        if tokens is not None:
            meta = QLabel(f"{tokens:,} tokens")
            meta.setObjectName("MetaLabel")
            header.addWidget(meta)

        if thinking_s is not None:
            think = QLabel(f"⏱ {thinking_s:.1f}s")
            think.setObjectName("MetaLabel")
            header.addWidget(think)

        layout.addLayout(header)

        sep = QFrame()
        sep.setObjectName("MsgSep")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        body = QLabel(content)
        body.setObjectName("MessageBody")
        body.setWordWrap(True)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(body)


class LogWindow(QWidget):
    def __init__(self, title, project, model, session_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Claude Log — {title[:60]}")
        self.resize(860, 680)
        self.setObjectName("LogWindow")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──
        header = QWidget()
        header.setObjectName("LogHeader")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(16, 10, 16, 10)
        hlay.setSpacing(16)

        def chip(text, name):
            lbl = QLabel(text)
            lbl.setObjectName(name)
            return lbl

        hlay.addWidget(chip(project, "HeaderProject"))
        hlay.addWidget(chip("│", "HeaderSep"))
        hlay.addWidget(chip(model, "HeaderModel"))
        hlay.addWidget(chip("│", "HeaderSep"))
        hlay.addWidget(chip(session_date, "HeaderDate"))
        hlay.addStretch()
        msg_count = QLabel(f"{len(DUMMY_MESSAGES)} messages")
        msg_count.setObjectName("HeaderMeta")
        hlay.addWidget(msg_count)

        root.addWidget(header)

        divider = QFrame()
        divider.setObjectName("HeaderDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(divider)

        # ── Scroll area ──
        scroll = QScrollArea()
        scroll.setObjectName("LogScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setObjectName("LogContainer")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(8)

        for role, ts, tokens, thinking_s, content in DUMMY_MESSAGES:
            bubble = MessageBubble(role, ts, tokens, thinking_s, content)
            vbox.addWidget(bubble)

        vbox.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)
