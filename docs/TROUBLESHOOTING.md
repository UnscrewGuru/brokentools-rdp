# Troubleshooting

## The app does not start

Run it from a terminal to see the error:

```
brokentools-rdp
```

- `No module named PyQt6` → install PyQt6 (see [INSTALL.md](INSTALL.md)).
- `command not found` after `install.sh` → add `~/.local/bin` to your `PATH`
  and open a new terminal.
- If FreeRDP is missing, install `freerdp` (it provides `xfreerdp`).

## Connection refused / timed out

- Is Remote Desktop switched on in Windows (Pro/Enterprise/Server only)?
- Test the port: `nc -zv HOST 3389`.
- Check the Windows firewall and that the PC is not asleep.
- Different network? Connect to your VPN first.

## Logon failed / wrong password

- Local account: user name `.\name`. Domain: `DOMAIN\name`. Microsoft account:
  the full email address.
- The account needs a password and permission to use Remote Desktop.
- NLA errors on very old servers: try an up-to-date Windows or check the
  FreeRDP version.

## Certificate warning

The first connection stores the server certificate. A later *certificate changed*
warning can be harmless (Windows reinstalled) or an attack. To accept a new
certificate for a host you trust, remove that host's entry from the known-hosts files under `~/.config/freerdp/`.

## Greek / non-Latin characters paste as `?`

A FreeRDP clipboard issue on Wayland. Workaround after copying in the remote
session, before pasting on Linux:

```
wl-paste --type "text/plain;charset=utf-8" | wl-copy
```

(requires the `wl-clipboard` package)

## Pasting a large image freezes the session

Known FreeRDP limitation: the session freezes for a few seconds. Enable
*Share my home folder* and open the file from the remote side instead.

## Full screen bar is missing

The bar needs the X11 client `xfreerdp`; `xfreerdp3` and the SDL client do not
show it. Use `Ctrl+Alt+Enter` to leave full screen.

## Reporting a bug

Open an issue on GitHub and include: distro, desktop environment (X11 or
Wayland), `xfreerdp --version`, and the terminal output.
