import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSplitter,
    QMessageBox
)
from PyQt6.QtCore import Qt

from ui.project_card import ProjectCard
from ui.session_card import SessionCard
from ui.log_window import LogWindow
from ui.import_dialog import ImportDialog
from core import jsonl_parser, config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude Log")
        self.setMinimumSize(800, 560)
        self.resize(1080, 700)
        self._log_windows: list[LogWindow] = []
        self._project_cards: list[ProjectCard] = []
        self._active_path: str | None = None

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
        import_btn.clicked.connect(self._import_project)
        tbar_lay.addWidget(import_btn)

        root.addWidget(toolbar)

        div = QFrame()
        div.setObjectName("ToolbarDivider")
        div.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(div)

        # ── Split panel ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("MainSplitter")
        splitter.setHandleWidth(1)

        # Left sidebar
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(180)
        sidebar.setMaximumWidth(300)
        sidebar_lay = QVBoxLayout(sidebar)
        sidebar_lay.setContentsMargins(0, 0, 0, 0)
        sidebar_lay.setSpacing(0)

        sidebar_hdr = QLabel("  PROJECTS")
        sidebar_hdr.setObjectName("SidebarHeader")
        sidebar_lay.addWidget(sidebar_hdr)

        proj_scroll = QScrollArea()
        proj_scroll.setObjectName("ProjectsScroll")
        proj_scroll.setWidgetResizable(True)
        proj_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._proj_container = QWidget()
        self._proj_container.setObjectName("ProjectsContainer")
        self._proj_lay = QVBoxLayout(self._proj_container)
        self._proj_lay.setContentsMargins(0, 4, 0, 4)
        self._proj_lay.setSpacing(1)
        self._proj_lay.addStretch()

        proj_scroll.setWidget(self._proj_container)
        sidebar_lay.addWidget(proj_scroll)

        splitter.addWidget(sidebar)

        # Right panel
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
        self._sessions_lay.addStretch()

        self._sessions_scroll.setWidget(self._sessions_container)
        right_lay.addWidget(self._sessions_scroll)

        splitter.addWidget(right)
        splitter.setSizes([220, 860])
        root.addWidget(splitter, 1)

        # ── Load persisted projects ──
        self._load_persisted_projects()

    # ── Project management ──────────────────────────────────────────────────

    def _load_persisted_projects(self):
        for proj in config.load_projects():
            path = proj["path"]
            name = proj["display_name"]
            if os.path.isdir(path):
                self._add_project_card(path, name)

    def _import_project(self):
        dlg = ImportDialog(self)
        if dlg.exec() != ImportDialog.DialogCode.Accepted:
            return
        path = dlg.selected_path()
        if not path or not os.path.isdir(path):
            return

        display_name = jsonl_parser.get_project_display_name(path)
        config.add_project(path, display_name)
        self._add_project_card(path, display_name)

    def _add_project_card(self, path: str, display_name: str):
        # Avoid duplicates
        for card in self._project_cards:
            if card.project_path == path:
                return

        sessions = jsonl_parser.scan_project(path)
        card = ProjectCard(display_name, len(sessions), path)
        card.clicked.connect(self._select_project)
        idx = self._proj_lay.count() - 1
        self._proj_lay.insertWidget(idx, card)
        self._project_cards.append(card)

        if self._active_path is None:
            self._select_project(path)

    def _select_project(self, path: str):
        self._active_path = path

        for card in self._project_cards:
            card.set_active(card.project_path == path)

        sessions = jsonl_parser.scan_project(path)
        display = next(
            (c.project_name for c in self._project_cards if c.project_path == path),
            path,
        )
        n = len(sessions)
        self._panel_header.setText(
            f"  {display}  —  {n} session{'s' if n != 1 else ''}"
        )

        # Rebuild session list
        while self._sessions_lay.count():
            item = self._sessions_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not sessions:
            empty = QLabel("No sessions found.")
            empty.setObjectName("EmptyLabel")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sessions_lay.addStretch()
            self._sessions_lay.addWidget(empty)
            self._sessions_lay.addStretch()
            return

        for meta in sessions:
            card = SessionCard(meta)
            card.clicked.connect(self._open_log)
            self._sessions_lay.addWidget(card)
        self._sessions_lay.addStretch()

    def _open_log(self, session_meta: dict):
        win = LogWindow(session_meta)
        win.show()
        self._log_windows.append(win)
