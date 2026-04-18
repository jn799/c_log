import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt


class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Project")
        self.setFixedWidth(520)
        self.setObjectName("ImportDialog")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        hint = QLabel(
            "Enter the path to a Claude Code project directory inside\n"
            "<tt>~/.claude/projects/</tt>"
        )
        hint.setObjectName("ImportHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        path_row = QHBoxLayout()
        self._path_edit = QLineEdit()
        self._path_edit.setObjectName("ImportPathEdit")
        self._path_edit.setPlaceholderText(
            "~/.claude/projects/-home-username-myproject"
        )
        self._path_edit.textChanged.connect(self._validate)

        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("BrowseButton")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse)

        path_row.addWidget(self._path_edit)
        path_row.addWidget(browse_btn)
        layout.addLayout(path_row)

        self._error_label = QLabel("")
        self._error_label.setObjectName("ImportError")
        layout.addWidget(self._error_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("DialogSep")
        layout.addWidget(sep)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.reject)

        self._ok_btn = QPushButton("Import")
        self._ok_btn.setObjectName("OkButton")
        self._ok_btn.setEnabled(False)
        self._ok_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self._ok_btn)
        layout.addLayout(btn_row)

    def _browse(self):
        default = os.path.expanduser("~/.claude/projects")
        chosen = QFileDialog.getExistingDirectory(
            self, "Select Claude project directory", default
        )
        if chosen:
            self._path_edit.setText(chosen)

    def _validate(self, text: str):
        path = os.path.expanduser(text.strip())
        if not text.strip():
            self._error_label.setText("")
            self._ok_btn.setEnabled(False)
            return
        if not os.path.isdir(path):
            self._error_label.setText("✗  Directory not found")
            self._ok_btn.setEnabled(False)
            return
        jsonls = [f for f in os.listdir(path) if f.endswith(".jsonl")]
        if not jsonls:
            self._error_label.setText("✗  No .jsonl session files found")
            self._ok_btn.setEnabled(False)
            return
        self._error_label.setText(f"✓  {len(jsonls)} session file{'s' if len(jsonls) != 1 else ''} found")
        self._error_label.setProperty("ok", True)
        self._ok_btn.setEnabled(True)

    def selected_path(self) -> str:
        return os.path.expanduser(self._path_edit.text().strip())
