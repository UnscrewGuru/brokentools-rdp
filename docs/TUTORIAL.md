# Tutorial - Your First Connection

This tutorial takes you from nothing to a working remote session in about
ten minutes. It assumes BrokenTools RDP is already installed
(see [INSTALL.md](INSTALL.md)).

## Step 1 - Prepare the Windows computer

On the Windows computer you want to control:

1. It must be **Windows 10/11 Pro, Enterprise or Education**, or Windows Server.
   Windows Home cannot be a remote desktop *host*.
2. Open **Settings → System → Remote Desktop** and switch **Remote Desktop** on.
   Confirm the prompt.
3. Note the computer's name or IP address. In a Command Prompt run `ipconfig`
   and read the *IPv4 Address* (for example `192.168.1.50`).
4. Make sure the Windows account you will use has a **password** and is allowed
   to connect (administrators are by default; others must be added under
   *Remote Desktop users*).
5. The computer must be awake. Disable sleep while you test.

## Step 2 - Check that you can reach it

On your Linux machine, in a terminal (replace the address):

```
ping 192.168.1.50
nc -zv 192.168.1.50 3389
```

`3389` is the RDP port. A message like *succeeded* means the way is open. If it
fails, check the Windows firewall and that both computers are on the same
network (or connected through a VPN).

## Step 3 - Open BrokenTools RDP

Start **BrokenTools RDP** from your application menu or run `brokentools-rdp`.
You will see a small window with **Computer**, **User name** and **Password**.

## Step 4 - Fill in the General tab

1. **Computer:** type the IP address or name, e.g. `192.168.1.50`.
   A custom port is written as `192.168.1.50:3390`.
2. **User name:** the Windows account. For a local account use `.\username`,
   for a Microsoft account use the email address, for a domain account use
   `DOMAIN\username`.
3. **Password:** your Windows password. It is never saved and is passed to
   FreeRDP privately, so it does not appear in the process list. If you leave
   it empty, FreeRDP asks for it when connecting.

## Step 5 - (Optional) Choose options

Click **Show Options** for more tabs:

- **Display:** window size or full screen.
- **Local Resources:** clipboard, sound, microphone, share your home folder.
- **Experience:** connection speed and visual effects.

The defaults are fine for a first try. Full details are in
[MANUAL.md](MANUAL.md).

## Step 6 - Connect

Press **Connect**. The first time, the server's certificate is remembered
(trust on first use, like SSH). A new window opens with the Windows desktop.

## Step 7 - Work in the session

- Type and click as normal. The clipboard works both ways for text.
- `Ctrl+Alt+Enter` toggles full screen.
- In full screen, a bar at the top lets you minimize, restore or close.
- To end the session, use Windows **Start → Disconnect** (keeps your programs
  running) or **Sign out** (closes them), or just close the window.

## Step 8 - Save the connection

Back in the main window choose **Save As...** to store the settings (without
the password) as an `.rdp` file. **Open...** loads it again, and files made by
Windows' own Remote Desktop Connection work too. The last 10 computers are also
remembered in the **Computer** drop-down.

## Connecting from outside your home network

Do **not** forward port 3389 on your router. Use a VPN instead (WireGuard,
Tailscale, ZeroTier or your company VPN), connect to it first, and then use the
Windows computer's VPN address in BrokenTools RDP.

## Next

- [MANUAL.md](MANUAL.md) - every setting explained
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - if something does not work
