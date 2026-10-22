# BrokenTools RDP - User Manual

Version 1.0.0

## What it is

BrokenTools RDP gives Linux the familiar *Remote Desktop Connection* window.
It collects your settings and starts **FreeRDP** (`xfreerdp` / `xfreerdp3`),
which does the actual remote desktop work. Your session opens in a normal
FreeRDP window.

## The main window

The window starts compact (Computer, User name, Password). **Show Options**
reveals four tabs; **Hide Options** collapses it again.

Buttons: **Save As...** saves an `.rdp` file, **Open...** loads one,
**Connect** starts the session.

### General

| Field | Meaning |
|---|---|
| Computer | Host name or IP address, optionally with `:port`. Remembers the last 10. |
| User name | `.\user` (local), `user@domain.com` (Microsoft/UPN) or `DOMAIN\user`. |
| Password | Used for this connection only. Never written to disk. Leave empty to be asked by FreeRDP when connecting. |

### Display

| Option | Meaning |
|---|---|
| Size | `Full screen` or a window size from 1024x768 up to 3840x2160 (1366x768, 1920x1080, 2560x1440, 3440x1440, 3840x1080 and more). Default 1280x720. |
| Resize the remote desktop when I resize the window | Dynamic resolution: the remote desktop follows the window size. The picture is also scaled (smart sizing). |
| Colour depth | 16, 24 or 32 bit. |

### Local Resources

| Option | Meaning |
|---|---|
| Clipboard | Copy and paste text and images between the two computers. |
| Remote audio playback | *Play on this computer* or *Do not play*. |
| Microphone | Send your microphone to the remote computer. |
| Share my home folder | Shows your Linux home folder in Windows as a drive (*Home on ...*). Leave off if you do not need it. |

### Experience

| Option | Meaning |
|---|---|
| Connection speed | Detect automatically, LAN (10 Mbps or higher), Broadband (2-10 Mbps) or Modem (56 Kbps). |
| Desktop background | Show or hide the wallpaper (hiding is faster on slow links). |
| Font smoothing | ClearType-style smooth text. |
| Visual styles | Windows themes on or off. |

## Keyboard shortcuts in a session

| Keys | Action |
|---|---|
| `Ctrl+Alt+Enter` | Toggle full screen |

In full screen, the top **connection bar** has minimize, restore and close.

## `.rdp` files

- **Save As...** writes the common fields (address, user name, size, options).
  The password is never included.
- **Open...** reads files from Windows too. Unknown fields are ignored.
- Start with a file: `brokentools-rdp connection.rdp`. The app also registers
  for the `application/x-rdp` file type so double-clicking `.rdp` files can open it.

## Where things are stored

| What | Where |
|---|---|
| Host and user-name history (last 10) | `~/.config/brokentools-rdp/recent.json` |
| Trusted server certificates | FreeRDP's own store (usually `~/.config/freerdp/`) |
| Passwords | Nowhere |

## Security notes

- The password is sent to FreeRDP through its standard input
  (`/args-from:stdin`), so other users cannot see it with `ps`.
- Server certificates are checked with **trust on first use**, like SSH. If you
  later get a *certificate changed* warning, find out why before continuing.
- Never expose port 3389 to the internet. Use a VPN or an RD Gateway.
- Sharing the home folder gives the remote computer access to your files. Only
  enable it with computers you trust.

## Command line

```
brokentools-rdp                  # open the window
brokentools-rdp connection.rdp   # open with a saved file
```

## Uninstall

See [INSTALL.md](INSTALL.md#method-b---installsh-any-distro-per-user) or run
`sudo pacman -R brokentools-rdp` if installed with `makepkg`.

## License and disclaimer

GPL-3.0-or-later. BrokenTools RDP is independent software and is not affiliated
with, endorsed by or sponsored by Microsoft. *Windows* and *Remote Desktop* are
trademarks of Microsoft Corporation. Thanks to the FreeRDP project.
