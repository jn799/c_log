# Phase 2: persist imported project paths to ~/.config/claude_log/projects.json
# and title cache to ~/.config/claude_log/titles.json

import os

CONFIG_DIR = os.path.expanduser("~/.config/claude_log")
PROJECTS_FILE = os.path.join(CONFIG_DIR, "projects.json")
TITLES_FILE = os.path.join(CONFIG_DIR, "titles.json")


def load_projects() -> list[str]:
    raise NotImplementedError("Phase 2")


def save_projects(paths: list[str]) -> None:
    raise NotImplementedError("Phase 2")
