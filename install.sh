#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

echo "Installing Claude Log..."

# Generate icon if not present
if [ ! -f "$SCRIPT_DIR/assets/icon.png" ]; then
    python3 "$SCRIPT_DIR/assets/generate_icon.py"
fi

mkdir -p "$APPS_DIR" "$ICONS_DIR"

# Write .desktop with absolute path to this install
sed "s|Exec=python3 .*main.py|Exec=python3 $SCRIPT_DIR/main.py|" \
    "$SCRIPT_DIR/claude_log.desktop" > "$APPS_DIR/claude_log.desktop"

cp "$SCRIPT_DIR/assets/icon.png" "$ICONS_DIR/claude_log.png"

# Refresh desktop database
update-desktop-database "$APPS_DIR" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo "Done. Claude Log is now in your application launcher."
echo "You can also run it directly: python3 $SCRIPT_DIR/main.py"
