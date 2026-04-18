from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSplitter, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from ui.project_card import ProjectCard
from ui.session_card import SessionCard
from ui.log_window import LogWindow

DUMMY_PROJECTS = {
    "~/wafer_trade": [
        {
            "title": "Fix the authentication bug in the payment flow",
            "date": "Today, 14:23",
            "msg_count": "6 messages",
            "model": "Sonnet 4.6",
            "project": "~/wafer_trade",
            "session_date": "2026-04-15 14:23",
        },
        {
            "title": "Refactor database connection pooling to use async context managers",
            "date": "Yesterday, 09:41",
            "msg_count": "12 messages",
            "model": "Sonnet 4.6",
            "project": "~/wafer_trade",
            "session_date": "2026-04-17 09:41",
        },
        {
            "title": "Add unit tests for the order service and mock the payment gateway",
            "date": "Apr 16, 22:05",
            "msg_count": "8 messages",
            "model": "Opus 4.7",
            "project": "~/wafer_trade",
            "session_date": "2026-04-16 22:05",
        },
    ],
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude Log")
        self.setMinimumSize(800, 560)
        self.resize(1060, 680)
        self._active_project = None
        self._active_project_card = None
        self._log_windows = []

        central = QWidget()
        central.setObjectName("Central")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ──
        toolbar = QWidget()
        toolbar.setObjectName("Toolbar")
        tbar_lay = QHBoxLayout(toolbar)
        tbar_lay.setContentsMargins(16, 10, 16, 10)
        tbar_lay.setSpacing(12)

        app_label = QLabel("CLAUDE LOG")
        app_label.setObjectName("AppTitle")

        tbar_lay.addWidget(app_label)
        tbar_lay.addStretch()

        import_btn = QPushButton("+ Import Project")
        import_btn.setObjectName("ImportButton")
        import_btn.setFixedHeight(30)
        tbar_lay.addWidget(import_btn)

        root.addWidget(toolbar)

        divider = QFrame()
        divider.setObjectName("ToolbarDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(divider)

        # ── Split panel ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("MainSplitter")
        splitter.setHandleWidth(1)

        # Left sidebar
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(180)
        sidebar.setMaximumWidth(280)
        sidebar_lay = QVBoxLayout(sidebar)
        sidebar_lay.setContentsMargins(0, 0, 0, 0)
        sidebar_lay.setSpacing(0)

        sidebar_header = QLabel("  PROJECTS")
        sidebar_header.setObjectName("SidebarHeader")
        sidebar_lay.addWidget(sidebar_header)

        projects_scroll = QScrollArea()
        projects_scroll.setObjectName("ProjectsScroll")
        projects_scroll.setWidgetResizable(True)
        projects_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        projects_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        projects_container = QWidget()
        projects_container.setObjectName("ProjectsContainer")
        self._projects_lay = QVBoxLayout(projects_container)
        self._projects_lay.setContentsMargins(0, 4, 0, 4)
        self._projects_lay.setSpacing(1)
        self._projects_lay.addStretch()

        projects_scroll.setWidget(projects_container)
        sidebar_lay.addWidget(projects_scroll)

        splitter.addWidget(sidebar)

        # Right content panel
        right = QWidget()
        right.setObjectName("RightPanel")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        self._panel_header = QLabel("  Select a project")
        self._panel_header.setObjectName("PanelHeader")
        right_lay.addWidget(self._panel_header)

        ph_div = QFrame()
        ph_div.setObjectName("PanelHeaderDiv")
        ph_div.setFrameShape(QFrame.Shape.HLine)
        right_lay.addWidget(ph_div)

        self._sessions_scroll = QScrollArea()
        self._sessions_scroll.setObjectName("SessionsScroll")
        self._sessions_scroll.setWidgetResizable(True)
        self._sessions_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._sessions_container = QWidget()
        self._sessions_container.setObjectName("SessionsContainer")
        self._sessions_lay = QVBoxLayout(self._sessions_container)
        self._sessions_lay.setContentsMargins(16, 12, 16, 12)
        self._sessions_lay.setSpacing(6)

        empty = QLabel("No project selected")
        empty.setObjectName("EmptyLabel")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sessions_lay.addStretch()
        self._sessions_lay.addWidget(empty)
        self._sessions_lay.addStretch()

        self._sessions_scroll.setWidget(self._sessions_container)
        right_lay.addWidget(self._sessions_scroll)

        splitter.addWidget(right)
        splitter.setSizes([220, 840])

        root.addWidget(splitter, 1)

        # Populate dummy data
        for project_name, sessions in DUMMY_PROJECTS.items():
            self._add_project_card(project_name, len(sessions), sessions)

        # Auto-select first project
        first = list(DUMMY_PROJECTS.keys())[0]
        self._select_project(first, DUMMY_PROJECTS[first])

    def _add_project_card(self, name, count, sessions):
        card = ProjectCard(name, count)
        card.clicked.connect(lambda n, s=sessions: self._select_project(n, s))
        # Insert before the trailing stretch
        idx = self._projects_lay.count() - 1
        self._projects_lay.insertWidget(idx, card)
        # Store reference for active state management
        card._sessions = sessions

    def _select_project(self, name, sessions):
        # Deactivate previous
        for i in range(self._projects_lay.count()):
            w = self._projects_lay.itemAt(i).widget()
            if isinstance(w, ProjectCard):
                w.set_active(w.project_name == name)

        self._panel_header.setText(f"  {name}  —  {len(sessions)} session{'s' if len(sessions) != 1 else ''}")
        self._active_project = name

        # Clear session panel
        while self._sessions_lay.count():
            item = self._sessions_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sd in sessions:
            card = SessionCard(sd)
            card.clicked.connect(self._open_log)
            self._sessions_lay.addWidget(card)

        self._sessions_lay.addStretch()

    def _open_log(self, session_data):
        win = LogWindow(
            title=session_data["title"],
            project=session_data["project"],
            model=session_data["model"],
            session_date=session_data["session_date"],
        )
        win.show()
        self._log_windows.append(win)
