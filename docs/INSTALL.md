# BrokenTools RDP - Installation Guide

BrokenTools RDP is a Remote Desktop client for Linux with the familiar
"Remote Desktop Connection" window. It is a PyQt6 front-end for FreeRDP.

This guide walks you through every way to install it. Pick **one** method.

| Method | Best for | Needs root? |
|---|---|---|
| A. `makepkg` package | Arch Linux, CachyOS, Manjaro, EndeavourOS | Only for pacman |
| B. `install.sh` | Any distro (per-user install) | Only to install dependencies |
| C. Run from source | Testing, development | Only to install dependencies |

## 0. Requirements

- A Linux desktop session (X11 or Wayland/XWayland)
- `python` 3.9 or newer
- PyQt6
- FreeRDP 2.x or 3.x providing `xfreerdp` (or `xfreerdp3`)

The Windows computer you connect to must run **Windows Pro, Enterprise or
Server** (Home edition cannot accept RDP connections) with Remote Desktop
enabled. See [TUTORIAL.md](TUTORIAL.md#step-1---prepare-the-windows-computer).

## 1. Get the files

Choose one:

**From the release archive** (this is the file you downloaded):

```
tar -xzf brokentools-rdp-1.0.0.tar.gz
cd brokentools-rdp-1.0.0
```

**From GitHub:**

```
git clone https://github.com/UnscrewGuru/brokentools-rdp.git
cd brokentools-rdp
```

## Method A - Arch Linux / CachyOS (recommended there)

1. Install the build tools once:
   ```
   sudo pacman -S --needed base-devel git
   ```
2. From inside the project folder run:
   ```
   makepkg -si
   ```
   `makepkg` builds the package and `-si` installs it with pacman, pulling in
   `python`, `python-pyqt6` and `freerdp` automatically.

   > The PKGBUILD downloads the tagged release (`v1.0.0`) from GitHub, so
   > this method works once that release is published. Until then use Method B.
3. Start it from the application menu (**BrokenTools RDP**) or run
   `brokentools-rdp`.

Remove it: `sudo pacman -R brokentools-rdp`

## Method B - `install.sh` (any distro, per user)

1. Open a terminal in the project folder.
2. Run (do **not** use `sudo`; the script asks for it only when it needs to
   install dependencies):
   ```
   bash install.sh
   ```
3. The script does three things:
   1. Installs FreeRDP and PyQt6 with `pacman`, `apt`, `dnf` or `zypper`
      (whichever it finds).
   2. Copies the program to `~/.local/share/brokentools-rdp`, the launcher to
      `~/.local/bin/brokentools-rdp` and the icon to your icon folder.
   3. Creates a menu entry.
4. Make sure `~/.local/bin` is in your `PATH` (most distros do this already).
   Check with `echo $PATH`. If it is missing add this line to `~/.bashrc`:
   ```
   export PATH="$HOME/.local/bin:$PATH"
   ```
5. Open **BrokenTools RDP** from the menu, or run `brokentools-rdp`.

Remove it:

```
bash uninstall.sh            # keeps your saved settings
bash uninstall.sh --purge    # also deletes ~/.config/brokentools-rdp
```

### Installing dependencies by hand

If `install.sh` does not know your package manager:

| Distro | Command |
|---|---|
| Arch / CachyOS | `sudo pacman -S freerdp python-pyqt6` |
| Debian / Ubuntu / Mint | `sudo apt install freerdp3-x11 python3-pyqt6` (older releases: `freerdp2-x11`) |
| Fedora | `sudo dnf install freerdp python3-pyqt6` |
| openSUSE | `sudo zypper install freerdp python3-qt6` |

Package names differ between distro versions. If one is not found, search with
your package manager (for example `apt search pyqt6`).

## Method C - Run from source (no install)

```
python3 brokentools_rdp.py
```

Install the dependencies first (table above).

## 2. Verify the installation

```
xfreerdp --version      # or: xfreerdp3 --version
python3 -c "import PyQt6; print('PyQt6 OK')"
brokentools-rdp         # the window should open
```

If the window opens, you are done. Continue with [TUTORIAL.md](TUTORIAL.md).

## 3. Updating

- Method A: get the new source and run `makepkg -si` again.
- Method B: get the new source and run `bash install.sh` again (it overwrites
  the old files; your settings are kept).

## Something went wrong?

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
