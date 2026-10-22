#!/bin/bash
# Removes the per-user install made by install.sh.
# Your saved connection history (~/.config/brokentools-rdp) is kept unless you pass --purge.
set -e

rm -rf "$HOME/.local/share/brokentools-rdp"
rm -f "$HOME/.local/bin/brokentools-rdp"
rm -f "$HOME/.local/share/applications/brokentools-rdp.desktop"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/brokentools-rdp.svg"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

if [ "$1" = "--purge" ]; then
    rm -rf "$HOME/.config/brokentools-rdp"
    echo "Removed BrokenTools RDP and its settings."
else
    echo "Removed BrokenTools RDP. (Settings kept; use --purge to remove them too.)"
fi
