#!/usr/bin/env python3
# BrokenTools RDP - a simple, familiar RDP client window for Linux.
# Copyright (C) 2026 Unscrew Guru
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# BrokenTools RDP is not affiliated with or endorsed by Microsoft.
# It is a front-end for FreeRDP (xfreerdp), which does the actual work.

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PyQt6.QtCore import QProcess
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFormLayout, QHBoxLayout,
    QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QTabWidget,
    QVBoxLayout, QWidget,
)

APP_NAME = "BrokenTools RDP"
APP_ID = "brokentools-rdp"
VERSION = "1.0.0"

CONFIG_DIR = Path.home() / ".config" / APP_ID
HISTORY_FILE = CONFIG_DIR / "recent.json"

SIZES = [
    "Full screen",
    "1024x768", "1280x720", "1366x768", "1440x900", "1600x900",
    "1680x1050", "1920x1080", "1920x1200",
    "2560x1080", "2560x1440", "2560x1600",
    "3440x1440", "3840x1080", "3840x2160",
]

# (label, FreeRDP /network value, value used in .rdp files)
SPEEDS = [
    ("Detect connection quality automatically", "auto", 7),
    ("LAN (10 Mbps or higher)", "lan", 6),
    ("Broadband (2 Mbps - 10 Mbps)", "broadband", 4),
    ("Modem (56 Kbps)", "modem", 1),
]


# ---------- icon ----------

def app_icon():
    """Use the installed icon; fall back to the SVG next to this script, then to a theme icon."""
    icon = QIcon.fromTheme(APP_ID)
    if not icon.isNull():
        return icon
    local = Path(__file__).resolve().with_name(f"{APP_ID}.svg")
    if local.exists():
        return QIcon(str(local))
    return QIcon.fromTheme("preferences-desktop-remote-desktop")


# ---------- FreeRDP helpers ----------

def find_freerdp():
    for name in ("xfreerdp3", "xfreerdp", "sdl-freerdp3", "sdl-freerdp"):
        path = shutil.which(name)
        if path:
            return path
    return None


def freerdp_major(exe):
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=5)
        m = re.search(r"version\s+(\d+)", out.stdout + out.stderr)
        return int(m.group(1)) if m else 3
    except Exception:
        return 3


def build_args(exe, major, s, password):
    """Return the FreeRDP arguments (without the program name).

    They are sent to FreeRDP through stdin (/args-from:stdin), so the password
    never appears in the process list.
    """
    a = [f"/v:{s['host']}"]
    if s["user"]:
        a.append(f"/u:{s['user']}")
    if password:
        a.append(f"/p:{password}")
    a.append("/cert:tofu" if major >= 3 else "/cert-tofu")
    a.append(f"/title:{s['host']} - {APP_NAME}")
    if s["size"] == "Full screen":
        a.append("/f")
        # Connection bar at the top of the screen (minimize / restore / close).
        # /floatbar exists only in the X11 client (xfreerdp).
        if "xfreerdp" in Path(exe).name:
            a.append("/floatbar:sticky:on,default:visible,show:fullscreen")
    else:
        a.append(f"/size:{s['size']}")
        if s["dynamic"]:
            a.append("/dynamic-resolution")
        else:
            a.append("/smart-sizing")
    a.append(f"/bpp:{s['bpp']}")
    a.append("+clipboard" if s["clipboard"] else "-clipboard")
    if s["audio"] == "local":
        a.append("/sound")
    if s["mic"]:
        a.append("/microphone")
    if s["drive"]:
        a.append(f"/drive:Home,{Path.home()}")
    a.append(f"/network:{s['speed']}")
    a.append("+wallpaper" if s["wallpaper"] else "-wallpaper")
    a.append("+fonts" if s["fonts"] else "-fonts")
    a.append("+themes" if s["themes"] else "-themes")
    return a


# ---------- .rdp files ----------

def write_rdp(path, s):
    speed_code = next(c for _, k, c in SPEEDS if k == s["speed"])
    full = s["size"] == "Full screen"
    w, h = (s["size"].split("x") if not full else ("1920", "1080"))
    lines = [
        f"full address:s:{s['host']}",
        f"username:s:{s['user']}",
        f"screen mode id:i:{2 if full else 1}",
        f"desktopwidth:i:{w}",
        f"desktopheight:i:{h}",
        f"session bpp:i:{s['bpp']}",
        f"dynamic resolution:i:{1 if s['dynamic'] else 0}",
        f"redirectclipboard:i:{1 if s['clipboard'] else 0}",
        f"audiomode:i:{0 if s['audio'] == 'local' else 2}",
        f"audiocapturemode:i:{1 if s['mic'] else 0}",
        f"drivestoredirect:s:{'*' if s['drive'] else ''}",
        f"connection type:i:{speed_code}",
        f"disable wallpaper:i:{0 if s['wallpaper'] else 1}",
        f"allow font smoothing:i:{1 if s['fonts'] else 0}",
        f"disable themes:i:{0 if s['themes'] else 1}",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_rdp(path):
    raw = {}
    for line in Path(path).read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3:
            raw[parts[0].strip().lower()] = parts[2].strip()

    def i(key, default):
        try:
            return int(raw.get(key, default))
        except ValueError:
            return default

    s = {"host": raw.get("full address", ""), "user": raw.get("username", "")}
    if i("screen mode id", 2) == 2:
        s["size"] = "Full screen"
    else:
        s["size"] = f"{i('desktopwidth', 1280)}x{i('desktopheight', 720)}"
    bpp = str(i("session bpp", 32))
    s["bpp"] = bpp if bpp in ("16", "24", "32") else "32"
    s["dynamic"] = i("dynamic resolution", 1) == 1
    s["clipboard"] = i("redirectclipboard", 1) == 1
    s["audio"] = "local" if i("audiomode", 0) == 0 else "off"
    s["mic"] = i("audiocapturemode", 0) == 1
    s["drive"] = bool(raw.get("drivestoredirect", ""))
    code = i("connection type", 7)
    s["speed"] = next((k for _, k, c in SPEEDS if c == code), "auto")
    s["wallpaper"] = i("disable wallpaper", 0) == 0
    s["fonts"] = i("allow font smoothing", 1) == 1
    s["themes"] = i("disable themes", 0) == 0
    return s


# ---------- Window ----------

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(460)
        self.proc = None
        self.pending_input = b""
        self.started_at = 0.0
        self.history = self.load_history()

        root = QVBoxLayout(self)

        # Banner
        banner = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(app_icon().pixmap(48, 48))
        title = QLabel("BrokenTools\nRDP")
        f = QFont()
        f.setPointSize(14)
        title.setFont(f)
        banner.addWidget(icon)
        banner.addWidget(title)
        banner.addStretch()
        root.addLayout(banner)

        # Tabs (shown after "Show Options")
        self.tabs = QTabWidget()
        self.tabs.addTab(self.build_general(), "General")
        self.tabs.addTab(self.build_display(), "Display")
        self.tabs.addTab(self.build_resources(), "Local Resources")
        self.tabs.addTab(self.build_experience(), "Experience")
        root.addWidget(self.tabs)

        # Simple (collapsed) form shown while options are hidden
        self.simple = self.build_simple()
        root.addWidget(self.simple)

        # Buttons
        row = QHBoxLayout()
        self.options_btn = QPushButton("Show Options")
        self.options_btn.clicked.connect(self.toggle_options)
        self.save_btn = QPushButton("Save As...")
        self.save_btn.clicked.connect(self.save_as)
        self.open_btn = QPushButton("Open...")
        self.open_btn.clicked.connect(lambda: self.open_file())
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setDefault(True)
        self.connect_btn.clicked.connect(self.connect_clicked)
        row.addWidget(self.options_btn)
        row.addStretch()
        row.addWidget(self.save_btn)
        row.addWidget(self.open_btn)
        row.addWidget(self.connect_btn)
        root.addLayout(row)

        self.options_visible = False
        self.apply_visibility()
        if self.history:
            self.fill_from_history(0)

    # --- tab builders ---
    def build_general(self):
        w = QWidget()
        form = QFormLayout(w)
        self.host_box = QComboBox()
        self.host_box.setEditable(True)
        self.host_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        for h in self.history:
            self.host_box.addItem(h["host"])
        self.host_box.setCurrentIndex(-1)
        self.host_box.activated.connect(self.fill_from_history)
        self.user_edit = QLineEdit()
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setPlaceholderText("Leave empty to be asked when connecting")
        form.addRow("Computer:", self.host_box)
        form.addRow("User name:", self.user_edit)
        form.addRow("Password:", self.pass_edit)
        note = QLabel("The password is never saved.")
        note.setEnabled(False)
        form.addRow("", note)
        return w

    def build_simple(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(0, 0, 0, 0)
        self.simple_host = QComboBox()
        self.simple_host.setEditable(True)
        self.simple_host.setModel(self.host_box.model())
        self.simple_host.setCurrentIndex(-1)
        self.simple_host.activated.connect(self.fill_from_history)
        self.simple_user = QLineEdit()
        form.addRow("Computer:", self.simple_host)
        form.addRow("User name:", self.simple_user)
        # keep the collapsed form and the General tab in sync
        self.simple_host.editTextChanged.connect(lambda t: self.host_box.setEditText(t))
        self.host_box.editTextChanged.connect(lambda t: self.simple_host.setEditText(t))
        self.simple_user.textChanged.connect(self.user_edit.setText)
        self.user_edit.textChanged.connect(self.simple_user.setText)
        return w

    def build_display(self):
        w = QWidget()
        form = QFormLayout(w)
        self.size_box = QComboBox()
        self.size_box.addItems(SIZES)
        self.size_box.setCurrentText("1280x720")  # a normal resizable window by default
        self.dynamic_chk = QCheckBox("Resize the remote desktop when I resize the window")
        self.dynamic_chk.setChecked(True)
        self.bpp_box = QComboBox()
        self.bpp_box.addItems(["16", "24", "32"])
        self.bpp_box.setCurrentText("32")
        form.addRow("Display size:", self.size_box)
        form.addRow("", self.dynamic_chk)
        form.addRow("Colors (bit):", self.bpp_box)
        tip = QLabel("Tip: Ctrl+Alt+Enter toggles full screen during a session.\n"
                     "In full screen, a connection bar appears at the top of the screen.")
        tip.setEnabled(False)
        form.addRow("", tip)
        return w

    def build_resources(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.clip_chk = QCheckBox("Clipboard")
        self.clip_chk.setChecked(True)
        self.drive_chk = QCheckBox("Share my home folder with the remote computer")
        self.mic_chk = QCheckBox("Microphone")
        self.audio_box = QComboBox()
        self.audio_box.addItems(["Play on this computer", "Do not play"])
        lay.addWidget(QLabel("Remote audio playback:"))
        lay.addWidget(self.audio_box)
        lay.addWidget(self.mic_chk)
        lay.addWidget(self.clip_chk)
        lay.addWidget(self.drive_chk)
        lay.addStretch()
        return w

    def build_experience(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel("Choose your connection speed to optimize performance:"))
        self.speed_box = QComboBox()
        for label, _, _ in SPEEDS:
            self.speed_box.addItem(label)
        self.wall_chk = QCheckBox("Desktop background")
        self.wall_chk.setChecked(True)
        self.font_chk = QCheckBox("Font smoothing")
        self.font_chk.setChecked(True)
        self.theme_chk = QCheckBox("Visual styles")
        self.theme_chk.setChecked(True)
        lay.addWidget(self.speed_box)
        lay.addWidget(self.wall_chk)
        lay.addWidget(self.font_chk)
        lay.addWidget(self.theme_chk)
        lay.addStretch()
        return w

    # --- show/hide options ---
    def apply_visibility(self):
        self.tabs.setVisible(self.options_visible)
        self.simple.setVisible(not self.options_visible)
        self.save_btn.setVisible(self.options_visible)
        self.open_btn.setVisible(self.options_visible)
        self.options_btn.setText("Hide Options" if self.options_visible else "Show Options")
        self.adjustSize()

    def toggle_options(self):
        self.options_visible = not self.options_visible
        self.apply_visibility()

    # --- settings <-> widgets ---
    def get_settings(self):
        return {
            "host": self.host_box.currentText().strip(),
            "user": self.user_edit.text().strip(),
            "size": self.size_box.currentText(),
            "dynamic": self.dynamic_chk.isChecked(),
            "bpp": self.bpp_box.currentText(),
            "clipboard": self.clip_chk.isChecked(),
            "audio": "local" if self.audio_box.currentIndex() == 0 else "off",
            "mic": self.mic_chk.isChecked(),
            "drive": self.drive_chk.isChecked(),
            "speed": SPEEDS[self.speed_box.currentIndex()][1],
            "wallpaper": self.wall_chk.isChecked(),
            "fonts": self.font_chk.isChecked(),
            "themes": self.theme_chk.isChecked(),
        }

    def set_settings(self, s):
        self.host_box.setEditText(s["host"])
        self.user_edit.setText(s["user"])
        if self.size_box.findText(s["size"]) < 0:  # resolution from a .rdp file that is not in the list
            self.size_box.addItem(s["size"])
        self.size_box.setCurrentText(s["size"])
        self.dynamic_chk.setChecked(s["dynamic"])
        self.bpp_box.setCurrentText(s["bpp"])
        self.clip_chk.setChecked(s["clipboard"])
        self.audio_box.setCurrentIndex(0 if s["audio"] == "local" else 1)
        self.mic_chk.setChecked(s["mic"])
        self.drive_chk.setChecked(s["drive"])
        idx = next((n for n, (_, k, _) in enumerate(SPEEDS) if k == s["speed"]), 0)
        self.speed_box.setCurrentIndex(idx)
        self.wall_chk.setChecked(s["wallpaper"])
        self.font_chk.setChecked(s["fonts"])
        self.theme_chk.setChecked(s["themes"])

    # --- history ---
    def load_history(self):
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def save_history(self, host, user):
        self.history = [h for h in self.history if h["host"] != host]
        self.history.insert(0, {"host": host, "user": user})
        self.history = self.history[:10]
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            HISTORY_FILE.write_text(json.dumps(self.history), encoding="utf-8")
        except Exception:
            pass

    def fill_from_history(self, index):
        if 0 <= index < len(self.history):
            self.host_box.setEditText(self.history[index]["host"])
            self.user_edit.setText(self.history[index]["user"])

    # --- actions ---
    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", str(Path.home() / "connection.rdp"),
                                              "RDP files (*.rdp)")
        if path:
            if not path.endswith(".rdp"):
                path += ".rdp"
            write_rdp(path, self.get_settings())

    def open_file(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open", str(Path.home()), "RDP files (*.rdp)")
        if path:
            try:
                self.set_settings(read_rdp(path))
            except Exception as e:
                QMessageBox.warning(self, APP_NAME, f"Could not read the file:\n{e}")

    def connect_clicked(self):
        s = self.get_settings()
        if not s["host"]:
            QMessageBox.information(self, APP_NAME, "Enter the name or IP address of the remote computer.")
            return
        exe = find_freerdp()
        if not exe:
            QMessageBox.critical(self, APP_NAME, "FreeRDP was not found.\nInstall it with:\nsudo pacman -S freerdp")
            return
        password = self.pass_edit.text()
        if not password:
            password, ok = QInputDialog.getText(
                self, APP_NAME, f"Password for {s['user'] or 'the remote user'}@{s['host']}:",
                QLineEdit.EchoMode.Password)
            if not ok:
                return
        self.save_history(s["host"], s["user"])
        args = build_args(exe, freerdp_major(exe), s, password)

        # Send all arguments (including the password) through stdin, one per line.
        self.pending_input = ("\n".join(args) + "\n").encode("utf-8")
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.proc.started.connect(self.send_arguments)
        self.proc.finished.connect(self.session_finished)
        self.started_at = time.monotonic()
        self.hide()
        self.proc.start(exe, ["/args-from:stdin"])

    def send_arguments(self):
        self.proc.write(self.pending_input)
        self.proc.closeWriteChannel()
        self.pending_input = b""

    def session_finished(self, code, _status):
        output = bytes(self.proc.readAll()).decode(errors="ignore")
        self.show()
        # If it ended quickly with an error, the connection most likely failed.
        if code != 0 and time.monotonic() - self.started_at < 10:
            tail = "\n".join(output.strip().splitlines()[-6:])
            QMessageBox.warning(self, APP_NAME,
                                "Could not connect to the remote computer.\n\n" + tail)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setDesktopFileName(APP_ID)
    win = MainWindow()
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".rdp"):
        win.open_file(sys.argv[1])
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
