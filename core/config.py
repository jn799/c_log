import json
import os
from datetime import datetime, timezone

_CONFIG_DIR = os.path.expanduser("~/.config/claude_log")
_PROJECTS_FILE = os.path.join(_CONFIG_DIR, "projects.json")
_TITLES_FILE = os.path.join(_CONFIG_DIR, "titles.json")


def _ensure_dir():
    os.makedirs(_CONFIG_DIR, exist_ok=True)


def load_projects() -> list[dict]:
    """Return list of {path, display_name} dicts."""
    try:
        with open(_PROJECTS_FILE) as f:
            data = json.load(f)
        return data.get("projects", [])
    except (OSError, json.JSONDecodeError):
        return []


def save_projects(projects: list[dict]) -> None:
    """Persist list of {path, display_name} dicts."""
    _ensure_dir()
    with open(_PROJECTS_FILE, "w") as f:
        json.dump({"projects": projects}, f, indent=2)


def add_project(path: str, display_name: str) -> list[dict]:
    """Add a project (idempotent by path). Returns updated list."""
    projects = load_projects()
    for p in projects:
        if p["path"] == path:
            p["display_name"] = display_name
            save_projects(projects)
            return projects
    projects.append({"path": path, "display_name": display_name})
    save_projects(projects)
    return projects


def remove_project(path: str) -> list[dict]:
    projects = [p for p in load_projects() if p["path"] != path]
    save_projects(projects)
    return projects


def load_titles() -> dict:
    """Return {session_uuid: title} cache."""
    try:
        with open(_TITLES_FILE) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_titles(titles: dict) -> None:
    _ensure_dir()
    with open(_TITLES_FILE, "w") as f:
        json.dump(titles, f, indent=2)


def cache_title(uuid: str, title: str) -> None:
    titles = load_titles()
    titles[uuid] = title
    save_titles(titles)


def get_cached_title(uuid: str) -> str | None:
    return load_titles().get(uuid)


_PINNED_FILE = os.path.join(_CONFIG_DIR, "pinned.json")


def set_last_accessed(path: str) -> None:
    projects = load_projects()
    ts = datetime.now(timezone.utc).isoformat()
    for p in projects:
        if p["path"] == path:
            p["last_accessed"] = ts
            break
    save_projects(projects)


def get_last_accessed(path: str) -> str:
    for p in load_projects():
        if p["path"] == path:
            return p.get("last_accessed", "")
    return ""


def load_pinned() -> set:
    try:
        with open(_PINNED_FILE) as f:
            return set(json.load(f).get("pinned", []))
    except (OSError, json.JSONDecodeError):
        return set()


def save_pinned(pinned: set) -> None:
    _ensure_dir()
    with open(_PINNED_FILE, "w") as f:
        json.dump({"pinned": list(pinned)}, f, indent=2)


def pin_session(uuid: str) -> None:
    pinned = load_pinned()
    pinned.add(uuid)
    save_pinned(pinned)


def unpin_session(uuid: str) -> None:
    pinned = load_pinned()
    pinned.discard(uuid)
    save_pinned(pinned)


def is_pinned(uuid: str) -> bool:
    return uuid in load_pinned()


def clear_project_titles(project_path: str) -> None:
    """Remove all cached titles for sessions in the given project directory."""
    titles = load_titles()
    if os.path.isdir(project_path):
        uuids = {
            os.path.splitext(f)[0]
            for f in os.listdir(project_path)
            if f.endswith(".jsonl")
        }
        updated = {k: v for k, v in titles.items() if k not in uuids}
        save_titles(updated)
