QSS = """
* {
    font-family: "JetBrains Mono", "Fira Mono", "Cascadia Code", "Courier New", monospace;
    font-size: 13px;
    color: #d4d4d4;
    selection-background-color: #3a3020;
    selection-color: #f0d090;
}

QMainWindow, QWidget#Central {
    background: #0e0e0e;
}

/* ── Toolbar ── */
QWidget#Toolbar {
    background: #111111;
    border-bottom: none;
}

QLabel#AppTitle {
    font-size: 24px;
    font-weight: bold;
    color: #c8915a;
    letter-spacing: 2px;
}

QLabel#AppSubtitle {
    font-size: 12px;
    color: #555555;
    letter-spacing: 1px;
}

QPushButton#ImportButton {
    background: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    color: #c8915a;
    padding: 0 12px;
    font-size: 12px;
}
QPushButton#ImportButton:hover {
    background: #2a2520;
    border-color: #c8915a;
}
QPushButton#ImportButton:pressed {
    background: #1a1510;
}

QFrame#ToolbarDivider, QFrame#PanelHeaderDiv, QFrame#HeaderDivider {
    background: #222222;
    border: none;
    max-height: 1px;
    min-height: 1px;
}

/* ── Splitter ── */
QSplitter#MainSplitter::handle {
    background: #222222;
    width: 1px;
}

/* ── Sidebar ── */
QWidget#Sidebar {
    background: #111111;
}

QLabel#SidebarHeader {
    background: #0e0e0e;
    color: #555555;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 8px 0;
    border-bottom: 1px solid #1e1e1e;
}

QScrollArea#ProjectsScroll, QScrollArea#SessionsScroll, QScrollArea#LogScroll {
    background: transparent;
    border: none;
}

QScrollArea#ProjectsScroll > QWidget > QWidget,
QScrollArea#SessionsScroll > QWidget > QWidget,
QScrollArea#LogScroll > QWidget > QWidget {
    background: transparent;
}

QScrollBar:vertical {
    background: #0e0e0e;
    width: 6px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #333333;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #555555; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

/* ── Bottom bar ── */
QWidget#BottomBar {
    background: #0a0a0a;
    border-top: 1px solid #1a1a1a;
}
QLabel#BottomCredit {
    color: #2a2a2a;
    font-size: 8px;
    letter-spacing: 1px;
}

/* ── Drag handle ── */
QLabel#DragHandle {
    color: transparent;
    font-size: 12px;
    min-width: 14px;
}
QFrame#ProjectCard[hovered="true"] QLabel#DragHandle {
    color: #444444;
}
QFrame#ProjectCard[active="true"] QLabel#DragHandle {
    color: #7a5535;
}

/* ── Last accessed label ── */
QLabel#ProjectLastAccessed {
    color: #3a3a3a;
    font-size: 10px;
}
QFrame#ProjectCard[active="true"] QLabel#ProjectLastAccessed {
    color: #5a4530;
}

/* ── Drop indicator ── */
QFrame#DropIndicator {
    background: #c8915a;
    border: none;
}

/* ── Pinned session card ── */
QFrame#SessionCard[pinned="true"] {
    background: #111820;
    border: 1px solid #1a2535;
    border-left: 2px solid #2a6080;
}
QLabel#PinIcon {
    color: #3a8090;
    font-size: 12px;
}

/* ── Trash button on project cards ── */
QPushButton#TrashBtn {
    background: transparent;
    border: none;
    color: #333333;
    font-size: 13px;
    border-radius: 3px;
    padding: 0;
}
QPushButton#TrashBtn:hover {
    background: #2a1010;
    color: #cc4444;
}

/* ── Refresh buttons ── */
QPushButton#RefreshBtn {
    background: transparent;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    color: #555555;
    font-size: 14px;
    padding: 0;
}
QPushButton#RefreshBtn:hover {
    background: #1e1e1e;
    border-color: #c8915a;
    color: #c8915a;
}

/* ── Panel header widget ── */
QWidget#PanelHeaderWidget {
    background: #111111;
}

/* ── Project cards ── */
QFrame#ProjectCard {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 2px 0;
}
QFrame#ProjectCard[active="true"] {
    background: #1e1a15;
    border-left: 2px solid #c8915a;
}
QFrame#ProjectCard[hovered="true"] {
    background: #181818;
}

QLabel#ProjectArrow {
    color: #444444;
    font-size: 9px;
}
QFrame#ProjectCard[active="true"] QLabel#ProjectArrow {
    color: #c8915a;
}

QLabel#ProjectName {
    color: #c0c0c0;
    font-size: 13px;
}
QFrame#ProjectCard[active="true"] QLabel#ProjectName {
    color: #f0d090;
}

QLabel#ProjectCount {
    background: #2a2a2a;
    color: #666666;
    font-size: 10px;
    padding: 1px 5px;
    border-radius: 8px;
    min-width: 16px;
}
QFrame#ProjectCard[active="true"] QLabel#ProjectCount {
    background: #4a3020;
    color: #e8a040;
    font-weight: bold;
}

/* ── Right panel ── */
QWidget#RightPanel { background: #0e0e0e; }

QLabel#PanelHeader {
    background: #111111;
    color: #888888;
    font-size: 11px;
    padding: 8px 0;
    letter-spacing: 1px;
    border-bottom: none;
}

QWidget#SessionsContainer { background: transparent; }

QLabel#EmptyLabel { color: #333333; font-size: 13px; }

/* ── Session cards ── */
QFrame#SessionCard {
    background: #141414;
    border: 1px solid #222222;
    border-radius: 4px;
}
QFrame#SessionCard[hovered="true"] {
    background: #1c1c1c;
    border-color: #333333;
}

QLabel#SessionTitle {
    color: #e8b850;
    font-size: 13px;
    font-weight: bold;
}
QLabel#SessionMeta {
    color: #555555;
    font-size: 11px;
}
QLabel#SessionModel {
    color: #7a5535;
    font-size: 11px;
    background: #1e1a12;
    padding: 1px 6px;
    border-radius: 3px;
}

QToolButton#CardMenuBtn {
    background: transparent;
    border: none;
    color: #333333;
    font-size: 14px;
    padding: 0 2px;
    border-radius: 3px;
}
QToolButton#CardMenuBtn:hover {
    background: #2a2a2a;
    color: #c8915a;
}
QToolButton#CardMenuBtn::menu-indicator { image: none; }

QMenu#CardMenu {
    background: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 4px 0;
}
QMenu#CardMenu::item {
    padding: 5px 16px;
    color: #c0c0c0;
    font-size: 12px;
}
QMenu#CardMenu::item:selected {
    background: #2a2520;
    color: #f0d090;
}

/* ── Log window ── */
QWidget#LogWindow { background: #0e0e0e; }

QWidget#LogHeader {
    background: #111111;
}

QLabel#HeaderProject {
    color: #c8915a;
    font-size: 13px;
    font-weight: bold;
}
QLabel#HeaderModel {
    color: #888888;
    font-size: 12px;
}
QLabel#HeaderDate {
    color: #666666;
    font-size: 12px;
}
QLabel#HeaderSep {
    color: #333333;
    font-size: 14px;
}
QLabel#HeaderMeta {
    color: #555555;
    font-size: 11px;
}

QWidget#LogContainer { background: transparent; }

QFrame#MessageBubble {
    background: #121212;
    border: 1px solid #1e1e1e;
    border-radius: 3px;
}
QFrame#MessageBubble[role="user"] {
    background: #0f1318;
    border-color: #1a2030;
}
QFrame#MessageBubble[role="assistant"] {
    background: #121212;
    border-color: #1e1e1e;
}

QLabel#RoleLabel {
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: bold;
    padding: 1px 6px;
    border-radius: 2px;
}
QLabel#RoleLabel[role="user"] {
    color: #5588cc;
    background: #0f1a2a;
}
QLabel#RoleLabel[role="assistant"] {
    color: #c8915a;
    background: #1e1208;
}

QLabel#TimestampLabel {
    color: #444444;
    font-size: 11px;
}

QLabel#MetaLabel {
    color: #555555;
    font-size: 11px;
    background: #1a1a1a;
    padding: 1px 6px;
    border-radius: 3px;
}

QFrame#MsgSep {
    background: #1e1e1e;
    border: none;
    max-height: 1px;
    min-height: 1px;
}

QLabel#MessageBody {
    color: #c8c8c8;
    font-size: 13px;
}

/* Phase 2 additions */

QLabel#ThinkingBadge {
    color: #666666;
    font-size: 10px;
    background: #1a1a1a;
    padding: 1px 6px;
    border-radius: 3px;
}

QLabel#ModelChip {
    color: #7a5535;
    font-size: 10px;
    background: #1e1a12;
    padding: 1px 6px;
    border-radius: 3px;
}

QLabel#EffortChip {
    color: #5588cc;
    font-size: 10px;
    background: #0f1a2a;
    padding: 1px 6px;
    border-radius: 3px;
}

QPushButton#ToolCallBadge {
    color: #888888;
    font-size: 11px;
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    padding: 2px 8px;
    border-radius: 3px;
    text-align: left;
}
QPushButton#ToolCallBadge:hover {
    background: #222222;
    border-color: #555555;
    color: #c0c0c0;
}
QPushButton#ToolCallBadge:checked {
    background: #1e1a12;
    border-color: #c8915a;
    color: #c8915a;
}

QFrame#ToolDetail {
    background: transparent;
    border: none;
}
QLabel#ToolDetailName {
    color: #c8915a;
    font-size: 11px;
    font-weight: bold;
}
QTextEdit#ToolDetailInput {
    background: #0a0a0a;
    border: 1px solid #2a2a2a;
    border-radius: 3px;
    color: #888888;
    font-size: 11px;
    selection-background-color: #3a3020;
}

QFrame#ToolExchangeSep {
    background: #0e0e0e;
    border: none;
}
QLabel#ToolExchangeLabel {
    color: #333333;
    font-size: 11px;
    font-style: italic;
}

QTextEdit#MessageBodyEdit {
    background: transparent;
    border: none;
    color: #c8c8c8;
    font-size: 13px;
    selection-background-color: #3a3020;
    selection-color: #f0d090;
}

/* Import dialog */
QDialog#ImportDialog {
    background: #141414;
}
QLabel#ImportHint {
    color: #888888;
    font-size: 12px;
}
QLineEdit#ImportPathEdit {
    background: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 3px;
    color: #d4d4d4;
    padding: 6px 8px;
    font-size: 12px;
}
QLineEdit#ImportPathEdit:focus {
    border-color: #c8915a;
}
QPushButton#BrowseButton, QPushButton#CancelButton {
    background: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    color: #888888;
    padding: 5px 10px;
    font-size: 12px;
}
QPushButton#BrowseButton:hover, QPushButton#CancelButton:hover {
    background: #282828;
    color: #d4d4d4;
}
QPushButton#OkButton {
    background: #2a1e10;
    border: 1px solid #c8915a;
    border-radius: 3px;
    color: #c8915a;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton#OkButton:hover {
    background: #3a2a18;
}
QPushButton#OkButton:disabled {
    background: #1a1a1a;
    border-color: #333333;
    color: #444444;
}
QLabel#ImportError {
    font-size: 11px;
    color: #cc5555;
    padding: 0 2px;
}
QLabel#ImportError[ok="true"] {
    color: #55aa55;
}
QLineEdit#SessionTitleEdit {
    background: #1e1e1e;
    border: 1px solid #c8915a;
    border-radius: 2px;
    color: #f0d090;
    font-size: 13px;
    font-weight: bold;
    padding: 0 4px;
    selection-background-color: #3a3020;
}

QFrame#DialogSep {
    background: #2a2a2a;
    border: none;
    max-height: 1px;
    min-height: 1px;
}

/* ── Report dialog ── */
QDialog#ReportDialog {
    background: #161616;
}
QLabel#ReportMessage {
    color: #c8c8c8;
    font-size: 13px;
    line-height: 1.6;
}
"""
