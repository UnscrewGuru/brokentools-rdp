#!/bin/bash
# BrokenTools RDP - per-user install (no root needed for the app itself).
# Run from the folder that contains this script:  bash install.sh
set -e

if [ "$EUID" -eq 0 ]; then
    echo "Do not run this as root. Run: bash install.sh"
    exit 1
fi

HERE="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/.local/share/brokentools-rdp"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

echo "==> 1/3 Dependencies (FreeRDP + PyQt6)"
if command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --needed --noconfirm freerdp python-pyqt6
elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get install -y freerdp3-x11 python3-pyqt6 || sudo apt-get install -y freerdp2-x11 python3-pyqt6
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y freerdp python3-pyqt6
elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y freerdp python3-qt6
else
    echo "Unknown package manager. Please install FreeRDP (xfreerdp) and PyQt6 yourself."
fi

echo "==> 2/3 Copying files"
mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"
cp "$HERE/brokentools_rdp.py" "$APP_DIR/brokentools_rdp.py"
cp "$HERE/brokentools-rdp.svg" "$ICON_DIR/brokentools-rdp.svg"

cat > "$BIN_DIR/brokentools-rdp" <<EOF
#!/bin/sh
exec python3 "$APP_DIR/brokentools_rdp.py" "\$@"
EOF
chmod +x "$BIN_DIR/brokentools-rdp"

echo "==> 3/3 Menu entry"
sed "s|^Exec=.*|Exec=$BIN_DIR/brokentools-rdp %f|" "$HERE/brokentools-rdp.desktop" > "$DESKTOP_DIR/brokentools-rdp.desktop"
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
gtk-update-icon-cache -q "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo
echo "Done! Search for 'BrokenTools RDP' in your application menu,"
echo "or run: $BIN_DIR/brokentools-rdp"
