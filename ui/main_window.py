import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSplitter,
    QMessageBox
)
from PyQt6.QtCore import Qt

from ui.project_card import ProjectCard
from ui.projects_container import ProjectsContainer
from ui.session_card import SessionCard
from ui.log_window import LogWindow
from ui.import_dialog import ImportDialog
from ui.report_dialog import ReportDialog
from core import jsonl_parser, config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLog")
        self.setMinimumSize(800, 560)
        self.resize(1080, 700)
        self._log_windows: list[LogWindow] = []
        self._project_cards: list[ProjectCard] = []
        self._session_cards: list[SessionCard] = []
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
        tbar_lay.setContentsMargins(16, 8, 16, 8)
        tbar_lay.setSpacing(12)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        app_label = QLabel("CLog")
        app_label.setObjectName("AppTitle")
        subtitle_label = QLabel("An Open-source Claude Code Log Viewer")
        subtitle_label.setObjectName("AppSubtitle")
        title_block.addWidget(app_label)
        title_block.addWidget(subtitle_label)
        tbar_lay.addLayout(title_block)
        tbar_lay.addStretch()

        update_all_btn = QPushButton("↻ Update All")
        update_all_btn.setObjectName("ImportButton")
        update_all_btn.setFixedHeight(30)
        update_all_btn.clicked.connect(self._update_all)
        tbar_lay.addWidget(update_all_btn)

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

        self._proj_container = ProjectsContainer()
        self._proj_container.reordered.connect(self._on_projects_reordered)
        proj_scroll.setWidget(self._proj_container)
        sidebar_lay.addWidget(proj_scroll)

        splitter.addWidget(sidebar)

        # Right panel
        right = QWidget()
        right.setObjectName("RightPanel")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        panel_header_widget = QWidget()
        panel_header_widget.setObjectName("PanelHeaderWidget")
        ph_lay = QHBoxLayout(panel_header_widget)
        ph_lay.setContentsMargins(0, 0, 8, 0)
        ph_lay.setSpacing(6)

        self._panel_header = QLabel("  Select a project")
        self._panel_header.setObjectName("PanelHeader")
        ph_lay.addWidget(self._panel_header, 1)

        refresh_btn = QPushButton("↻")
        refresh_btn.setObjectName("RefreshBtn")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setToolTip("Refresh current project")
        refresh_btn.clicked.connect(self._refresh_current_project)
        ph_lay.addWidget(refresh_btn)

        right_lay.addWidget(panel_header_widget)

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

        # ── Bottom bar ──
        bottom = QWidget()
        bottom.setObjectName("BottomBar")
        bot_lay = QHBoxLayout(bottom)
        bot_lay.setContentsMargins(12, 4, 12, 4)
        bot_lay.addStretch()
        credit = QLabel("Developed using Claude Code, by Joe Nguyen")
        credit.setObjectName("BottomCredit")
        bot_lay.addWidget(credit)
        root.addWidget(bottom)

        self._load_persisted_projects()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _update_panel_header(self):
        if not self._active_path:
            return
        display = next(
            (c.project_name for c in self._project_cards if c.project_path == self._active_path),
            self._active_path,
        )
        n = len(self._session_cards)
        total_tok = sum(c.session_meta.get("total_tokens", 0) for c in self._session_cards)
        tok_str = jsonl_parser._fmt_tokens(total_tok) if total_tok else ""
        tok_part = f"  ·  {tok_str}" if tok_str else ""
        self._panel_header.setText(f"  {display}  —  {n} session{'s' if n != 1 else ''}{tok_part}")

    def _clear_sessions_layout(self):
        while self._sessions_lay.count():
            item = self._sessions_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._session_cards = []

    def _build_session_list(self, sessions: list[dict]):
        self._clear_sessions_layout()
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
            card.updated.connect(self._on_session_updated)
            card.pin_changed.connect(self._on_pin_changed)
            self._sessions_lay.addWidget(card)
            self._session_cards.append(card)
        self._sessions_lay.addStretch()

    # ── Project management ─────────────────────────────────────────────────────

    def _load_persisted_projects(self):
        for proj in config.load_projects():
            path = proj["path"]
            name = proj["display_name"]
            last = proj.get("last_accessed", "")
            if os.path.isdir(path):
                self._add_project_card(path, name, last)

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

    def _add_project_card(self, path: str, display_name: str, last_accessed: str = ""):
        for card in self._project_cards:
            if card.project_path == path:
                return
        sessions = jsonl_parser.scan_project(path)
        card = ProjectCard(display_name, len(sessions), path, last_accessed)
        card.clicked.connect(self._select_project)
        card.remove_requested.connect(self._remove_project)
        self._proj_container.add_card(card)
        self._project_cards.append(card)
        if self._active_path is None:
            self._select_project(path)

    def _select_project(self, path: str):
        self._active_path = path
        for card in self._project_cards:
            card.set_active(card.project_path == path)

        config.set_last_accessed(path)
        ts = config.get_last_accessed(path)
        for card in self._project_cards:
            if card.project_path == path:
                card.update_last_accessed(ts)
                break

        sessions = jsonl_parser.scan_project(path)
        pinned_uuids = config.load_pinned()
        pinned = [s for s in sessions if s["uuid"] in pinned_uuids]
        unpinned = [s for s in sessions if s["uuid"] not in pinned_uuids]
        self._build_session_list(pinned + unpinned)
        self._update_panel_header()

    def _remove_project(self, path: str):
        reply = QMessageBox.warning(
            self,
            "Remove Project",
            "Removing this project will permanently delete all custom session names you've set.\n\n"
            "If you re-import the project, sessions will revert to their original titles "
            "(the first message in each session).\n\n"
            "Remove from view?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        config.clear_project_titles(path)
        config.remove_project(path)

        for card in self._project_cards:
            if card.project_path == path:
                self._proj_container.remove_card(card)
                card.deleteLater()
                self._project_cards.remove(card)
                break

        if self._active_path == path:
            self._active_path = None
            self._clear_sessions_layout()
            self._sessions_lay.addStretch()
            self._panel_header.setText("  Select a project")
            if self._project_cards:
                self._select_project(self._project_cards[0].project_path)

    def _on_projects_reordered(self, paths: list):
        projects = config.load_projects()
        by_path = {p["path"]: p for p in projects}
        config.save_projects([by_path[p] for p in paths if p in by_path])
        self._project_cards = [c for p in paths for c in self._project_cards if c.project_path == p]

    # ── Refresh / update ───────────────────────────────────────────────────────

    def _refresh_current_project(self):
        if not self._active_path:
            return
        old_count = len(self._session_cards)
        old_tok = sum(c.session_meta.get("total_tokens", 0) for c in self._session_cards)
        old_by_uuid = {
            c.session_meta["uuid"]: c.session_meta
            for c in self._session_cards
        }

        self._select_project(self._active_path)

        new_count = len(self._session_cards)
        new_tok = sum(c.session_meta.get("total_tokens", 0) for c in self._session_cards)
        sessions_changed = sum(
            1 for c in self._session_cards
            if c.session_meta["uuid"] in old_by_uuid and (
                c.session_meta.get("total_tokens", 0)
                != old_by_uuid[c.session_meta["uuid"]].get("total_tokens", 0)
                or c.session_meta.get("msg_count", "")
                != old_by_uuid[c.session_meta["uuid"]].get("msg_count", "")
            )
        )

        changes = []
        if new_count != old_count:
            diff = new_count - old_count
            changes.append(f"Sessions:  {old_count}  →  {new_count}  ({'+' if diff>0 else ''}{diff})")
        if sessions_changed:
            changes.append(f"{sessions_changed} session{'s' if sessions_changed != 1 else ''} had new activity")
        if new_tok != old_tok:
            changes.append(
                f"Tokens:  {jsonl_parser._fmt_tokens(old_tok) if old_tok else '0'}"
                f"  →  {jsonl_parser._fmt_tokens(new_tok) if new_tok else '0'}"
            )
        if changes:
            ReportDialog.show("Project Refreshed", "Updated:\n\n• " + "\n• ".join(changes), self)
        else:
            ReportDialog.show("Project Refreshed", "Already up-to-date!", self)

    def _update_all(self):
        proj_changes = []
        for card in self._project_cards:
            old = card._session_count
            sessions = jsonl_parser.scan_project(card.project_path)
            new = len(sessions)
            card.update_count(new)
            if new != old:
                diff = new - old
                proj_changes.append(
                    f"{card.project_name}:  {old}  →  {new} sessions  ({'+' if diff>0 else ''}{diff})"
                )
        if self._active_path:
            self._select_project(self._active_path)
        if proj_changes:
            ReportDialog.show("Update All", "Projects updated:\n\n• " + "\n• ".join(proj_changes), self)
        else:
            ReportDialog.show("Update All", "All projects are already up-to-date!", self)

    def _on_session_updated(self, _new_meta: dict):
        self._update_panel_header()

    def _on_pin_changed(self):
        if self._active_path:
            self._select_project(self._active_path)

    # ── Open log window ────────────────────────────────────────────────────────

    def _open_log(self, session_meta: dict):
        win = LogWindow(session_meta)
        win.show()
        self._log_windows.append(win)
