# CLog

**An open-source GUI log viewer for [Claude Code](https://claude.ai/code) sessions.**

Browse, search, and explore your Claude Code conversation history — message by message, with token counts, tool call details, effort levels, and more.

![Main view](assets/screenshots/main_view.png)

---

## Features

- **Browse all projects and sessions** from your Claude Code history
- **Per-message detail** — model, effort level, token count, thinking badges
- **Tool call inspector** — click any tool badge to expand its input
- **Token accounting** — per-session and per-project token totals
- **Session management** — rename sessions, pin important ones to the top
- **Drag-to-reorder** projects in the sidebar
- **Update / refresh** — re-read JSONL files and report what changed
- **Dark theme** with a clean monospace aesthetic

---

## Requirements

- Python 3.10+
- PyQt6

```bash
pip install PyQt6
```

---

## Installation

```bash
git clone https://github.com/jn799/clog.git
cd clog
pip install -r requirements.txt
python3 main.py
```

On first launch, click **+ Import Project** and point it at a Claude Code project directory (typically `~/.claude/projects/<project-name>/`).

---

## Usage

### Importing a project

Click **+ Import Project** in the toolbar. Navigate to any directory containing Claude Code `.jsonl` session files.

### Browsing sessions

Click a project in the sidebar to list its sessions. Sessions are sorted by most recent activity, with pinned sessions at the top.

### Viewing a session

Click any session card to open the full conversation log. Tool calls are expandable — click a tool badge to see its inputs.

### Renaming a session

Click the **⋯** menu on a session card → **Rename**.

### Pinning a session

Click the **⋯** menu → **Pin**. Pinned sessions stay at the top of the list regardless of activity time.

### Updating stats

- **Per session** — ⋯ menu → **Update** to re-read that session's file and report changes.
- **Current project** — click **↻** in the panel header.
- **All projects** — click **↻ Update All** in the toolbar.

### Reordering projects

Drag the **⠿** handle on any project card to reorder. Order is saved automatically.

### Removing a project

Click the **🗑** icon on a project card. Note: this removes the project from CLog's view only — no files are deleted from disk.

---

## Data & Privacy

CLog reads your Claude Code session logs **locally only**. No data is sent anywhere. Config is stored in `~/.config/claude_log/`.

---

## Contributing

Pull requests are welcome. For major changes, open an issue first.

---

## License

MIT — see [LICENSE](LICENSE).
