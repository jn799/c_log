# Claude Log Viewer — Project Brief

## What This Is

A desktop GUI tool for Linux that reads Claude Code's local conversation history from `~/.claude/projects/` (JSONL files), displays them in a browsable interface grouped by project, and renders each conversation in a readable format. Read-only — no chat interaction, purely a history viewer.

**Repo location:** `~/claude_log/`
**Target OS:** Linux only (for now)
**Open-source:** Yes, eventually on GitHub

---

## Tech Stack Decision

**Python + PyQt6**

- JSONL parsing is trivial in Python
- PyQt6 QSS (Qt Style Sheets) can achieve the desired pixel-art / monospace terminal aesthetic
- Multi-window support (conversation pop-outs) is clean in Qt
- Best packaging story for Linux open-source (pip, .deb, Flatpak)
- Low barrier for contributors

---

## Aesthetic / UX Requirements

- Monospace font throughout, pixel art style — looks like Claude Code in the terminal
- Each conversation window header shows session metadata: Claude Code version, model (Claude Pro / Opus / Sonnet), project name
- Each message shows timestamp + date (like Messenger/WhatsApp/Telegram)
- Each assistant message shows token count and time spent thinking (if available in JSONL)
- Titles for sessions are derived from the first user message (truncated ~80 chars), not raw session UUIDs

---

## Layout (Agreed Design)

**Main window — sidebar + content panel** (VS Code / Slack style, NOT nested screens):

```
┌─────────────────────────────────────────────────┐
│  [Import Project]                                │
├──────────────┬──────────────────────────────────┤
│ Projects     │  Sessions in selected project     │
│ ──────────── │  ──────────────────────────────  │
│ ~/wafer_trade│  [Session card: first msg title]  │
│ ~/rmf_ws     │  [Session card: first msg title]  │
│              │  [Session card: first msg title]  │
│              │                                   │
└──────────────┴──────────────────────────────────┘
```

Clicking a session card opens a **new window** with the full conversation log.

---

## Import Flow

- "Import Project" button → opens text input dialog (or file browser)
- User enters path like `~/.claude/projects/-home-hplaptopjoseph-wafer-trade`
- App validates path, finds `.jsonl` files, parses them
- Project card appears in sidebar with reformatted name: `~/wafer_trade`
- Imported paths are persisted in `~/.config/claude_log/projects.json`

---

## Build Phases

### Phase 1 — GUI Skeleton (start here)
- Main window with sidebar + content panel layout
- Hardcoded dummy project card: `~/wafer_trade`
- 3 dummy session cards inside with placeholder titles
- Clicking a session card opens a pop-out log window with lorem ipsum in monospace
- Hardcoded dummy session metadata header at top of log window
- `.desktop` launcher file created and working
- `install.sh` script that drops `.desktop` + icon into `~/.local/share/`

### Phase 2 — Import + Parsing
- "Import Project" button functional
- JSONL parser: extract messages, timestamps, token counts, model/version metadata
- Title generation from first user message (cached to `~/.config/claude_log/titles.json`)
- Real conversation rendering: timestamps, role labels, token counts
- Config persistence

### Phase 3 — Refresh / Update
- Refresh icon button on each project card
- Detect new JSONL files and grown files (resumed sessions via `claude --resume`)
- Badge showing count of new/updated sessions
- Re-parse updated sessions, update title cache

---

## Repo Structure (Target)

```
~/claude_log/
├── main.py                  # Entry point
├── ui/
│   ├── main_window.py       # Sidebar + content panel
│   ├── project_card.py      # Project card widget
│   ├── session_card.py      # Session card widget
│   └── log_window.py        # Conversation viewer (pop-out window)
├── core/
│   ├── jsonl_parser.py      # Parse JSONL, extract messages + metadata
│   └── config.py            # Load/save imported project paths
├── assets/
│   └── icon.png             # App icon (pixel art, 256x256)
├── claude_log.desktop       # Desktop launcher file
├── install.sh               # Installs .desktop + icon to ~/.local/share/
├── requirements.txt         # PyQt6 (and any others)
└── README.md
```

---

## Open Questions (Decide Before Phase 2)

| Question | Options | Status |
|---|---|---|
| Session title source | First user message (offline, simple) vs. Claude API call (requires key) | Prefer first-message for now |
| Tool call rendering | Collapsed label / hidden / shown inline | TBD |
| Thinking blocks | Hidden by default with toggle / always hidden | TBD |
| Large file handling | Lazy load / paginate / load full on open | TBD |

---

## Key Data Notes

- JSONL files live at: `~/.claude/projects/<encoded-path>/<session-uuid>.jsonl`
- Each line in a JSONL is a JSON object representing one event (user message, assistant message, tool call, tool result, thinking block, etc.)
- `usage` field on assistant messages contains token counts
- `model` and `version` fields are present in message metadata
- Sessions may contain sensitive data (pasted secrets, API keys) — note in README

---

## Config / State Files

- Imported project list: `~/.config/claude_log/projects.json`
- Title cache: `~/.config/claude_log/titles.json`
- XDG-compliant paths throughout

---

## Desktop Launcher

Need to create:
- `assets/icon.png` — 256×256 pixel art icon
- `claude_log.desktop` — standard `.desktop` format pointing to `main.py`
- `install.sh` — copies both to `~/.local/share/applications/` and `~/.local/share/icons/`

---

## Out of Scope (for now)

- Windows and macOS support
- Adding new messages / interacting with Claude
- Sharing or exporting conversations
- Dark/light theme toggle (pick one and commit)
