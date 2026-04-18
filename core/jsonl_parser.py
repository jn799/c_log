import json
import os
from datetime import datetime, timezone, timedelta

_HOME = os.path.expanduser("~")
_TODAY = datetime.now(timezone.utc).date()


def _display_path(cwd: str) -> str:
    if cwd and cwd.startswith(_HOME):
        return "~" + cwd[len(_HOME):]
    return cwd or ""


def _fmt_ts(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        local = dt.astimezone()
        d = local.date()
        t = local.strftime("%H:%M")
        delta = (_TODAY - d).days
        if delta == 0:
            return f"Today, {t}"
        if delta == 1:
            return f"Yesterday, {t}"
        if delta < 7:
            return f"{d.strftime('%a')}, {t}"
        return f"{d.strftime('%b %-d')}, {t}"
    except Exception:
        return iso[:16] if iso else ""


def _fmt_ts_long(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso[:16] if iso else ""


def _extract_user_text(content) -> str:
    """Plain text from a user message content field (str or list of blocks)."""
    if isinstance(content, str):
        return content.strip()
    texts = [
        b.get("text", "")
        for b in content
        if isinstance(b, dict) and b.get("type") == "text"
    ]
    return "\n".join(texts).strip()


def _is_human_text(text: str) -> bool:
    """Return True if the text looks like a real human message, not a system injection."""
    t = text.strip()
    if not t or len(t) < 3:
        return False
    # System-injected XML blocks used by Claude Code harness
    system_prefixes = (
        "<local-command-caveat>",
        "<command-name>",
        "<command-message>",
        "<command-args>",
        "<local-command-stdout>",
        "<local-command-stderr>",
        "<bash-input>",
        "<bash-stdout>",
        "<bash-stderr>",
        "<task-notification>",
        "<system-reminder>",
        "<function_calls>",
        "<function_calls>",
    )
    return not any(t.startswith(p) for p in system_prefixes)


def _is_tool_result_only(content) -> bool:
    if not isinstance(content, list) or not content:
        return False
    return all(
        isinstance(b, dict) and b.get("type") == "tool_result"
        for b in content
    )


# ──────────────────────────────────────────────────────────────────────────────

def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M tok"
    if n >= 1_000:
        return f"{n/1_000:.1f}k tok"
    return f"{n} tok"


def parse_session_metadata(path: str) -> dict | None:
    """
    Fast scan: returns a dict with keys:
        uuid, title, custom_title, first_ts, last_ts, model, version,
        cwd, display_path, msg_count, total_tokens
    Returns None if the file is empty or unparseable.
    title    — first human user message (fallback)
    custom_title — value from Claude Code's custom-title event (may be "")
    """
    uuid = os.path.splitext(os.path.basename(path))[0]
    title = ""
    custom_title = ""
    first_ts = last_ts = ""
    model = version = cwd = ""
    msg_count = 0
    total_tokens = 0

    try:
        for raw in open(path):
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue

            t = ev.get("type")

            if t == "user":
                content = ev.get("message", {}).get("content", "")
                if not _is_tool_result_only(content):
                    text = _extract_user_text(content)
                    if _is_human_text(text):
                        msg_count += 1
                        if not title:
                            title = text[:80] + ("…" if len(text) > 80 else "")
                if not first_ts:
                    first_ts = ev.get("timestamp", "")
                if not version:
                    version = ev.get("version", "")
                if not cwd:
                    cwd = ev.get("cwd", "")
                last_ts = ev.get("timestamp", last_ts)

            elif t == "assistant":
                msg_content = ev.get("message", {}).get("content", [])
                has_text = any(
                    isinstance(b, dict) and b.get("type") in ("text", "tool_use")
                    for b in msg_content
                )
                if has_text:
                    msg_count += 1
                usage = ev.get("message", {}).get("usage", {})
                total_tokens += (usage.get("output_tokens") or 0)
                if not model:
                    model = ev.get("message", {}).get("model", "")
                last_ts = ev.get("timestamp", last_ts)

            elif t == "custom-title":
                custom_title = ev.get("customTitle", "")

    except OSError:
        return None

    if not title and not first_ts:
        return None

    return {
        "uuid": uuid,
        "path": path,
        "title": title or f"Session {uuid[:8]}",
        "custom_title": custom_title,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "date": _fmt_ts(last_ts or first_ts),
        "date_sort": last_ts or first_ts,
        "model": _normalize_model(model),
        "version": version,
        "cwd": cwd,
        "display_path": _display_path(cwd),
        "msg_count": f"{msg_count} message{'s' if msg_count != 1 else ''}",
        "total_tokens": total_tokens,
        "total_tokens_fmt": _fmt_tokens(total_tokens) if total_tokens else "",
    }


def _normalize_model(raw: str) -> str:
    if not raw or raw == "<synthetic>":
        return ""
    r = raw.lower()
    if "opus" in r:
        return "Opus"
    if "sonnet" in r:
        return "Sonnet"
    if "haiku" in r:
        return "Haiku"
    return ""


# ──────────────────────────────────────────────────────────────────────────────

def _extract_effort(content) -> str | None:
    """Extract effort level from a /effort command user message, or None."""
    text = content if isinstance(content, str) else _extract_user_text(content)
    if "<command-name>/effort</command-name>" not in text:
        return None
    import re
    m = re.search(r"<command-args>(.*?)</command-args>", text)
    return m.group(1).strip().lower() if m else None


def parse_session_messages(path: str) -> list[dict]:
    """
    Full parse. Returns a list of message dicts:
        role, timestamp, text, tool_calls, thinking, output_tokens, model, effort, is_tool_exchange
    Consecutive thinking+response assistant events are merged into one.
    """
    events = []
    try:
        for raw in open(path):
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if ev.get("type") in ("user", "assistant"):
                events.append(ev)
    except OSError:
        return []

    messages = []
    pending_thinking = False
    current_effort: str | None = None

    for ev in events:
        t = ev.get("type")
        ts = ev.get("timestamp", "")
        version = ev.get("version", "")

        if t == "user":
            pending_thinking = False
            content = ev.get("message", {}).get("content", "")
            effort = _extract_effort(content)
            if effort is not None:
                current_effort = effort
            is_tool = _is_tool_result_only(content)
            text = "" if is_tool else _extract_user_text(content)
            # Skip system-injected messages that aren't real human input
            if not is_tool and not _is_human_text(text):
                continue
            messages.append({
                "role": "user",
                "timestamp": _fmt_ts_long(ts),
                "text": text,
                "tool_calls": [],
                "thinking": False,
                "output_tokens": None,
                "model": None,
                "effort": None,
                "version": version,
                "is_tool_exchange": is_tool,
            })

        elif t == "assistant":
            msg_content = ev.get("message", {}).get("content", [])
            content_types = {
                b.get("type") for b in msg_content if isinstance(b, dict)
            }

            # Thinking-only block — buffer it and skip to next event
            if content_types == {"thinking"}:
                pending_thinking = True
                continue

            text_blocks = [
                b.get("text", "")
                for b in msg_content
                if isinstance(b, dict) and b.get("type") == "text"
            ]
            tool_calls = [
                {"name": b.get("name", ""), "input": b.get("input", {})}
                for b in msg_content
                if isinstance(b, dict) and b.get("type") == "tool_use"
            ]

            usage = ev.get("message", {}).get("usage", {})

            messages.append({
                "role": "assistant",
                "timestamp": _fmt_ts_long(ts),
                "text": "\n\n".join(text_blocks),
                "tool_calls": tool_calls,
                "thinking": pending_thinking,
                "output_tokens": usage.get("output_tokens"),
                "model": _normalize_model(ev.get("message", {}).get("model", "")),
                "effort": current_effort,
                "version": version,
                "is_tool_exchange": False,
            })
            pending_thinking = False

    return messages


# ──────────────────────────────────────────────────────────────────────────────

def get_project_display_name(project_dir: str) -> str:
    """
    Derive a display name for a project directory by reading cwd from the
    first user event found. Falls back to decoding the directory name.
    """
    for fname in sorted(os.listdir(project_dir)):
        if not fname.endswith(".jsonl"):
            continue
        fpath = os.path.join(project_dir, fname)
        try:
            for raw in open(fpath):
                raw = raw.strip()
                if not raw:
                    continue
                ev = json.loads(raw)
                if ev.get("type") == "user" and ev.get("cwd"):
                    return _display_path(ev["cwd"])
        except Exception:
            continue
    # Fallback: decode the encoded directory name
    name = os.path.basename(project_dir)
    if name.startswith("-home-"):
        parts = name.split("-", 3)  # ["-", "home", "username", "rest"]
        if len(parts) >= 4:
            rest = parts[3].replace("-", "/")
            return f"~/{rest}"
    return name


def scan_project(project_dir: str) -> list[dict]:
    """Return sorted list of session metadata dicts for all JSONL files."""
    sessions = []
    for fname in os.listdir(project_dir):
        if not fname.endswith(".jsonl"):
            continue
        meta = parse_session_metadata(os.path.join(project_dir, fname))
        if meta:
            sessions.append(meta)
    sessions.sort(key=lambda s: s["date_sort"], reverse=True)
    return sessions
