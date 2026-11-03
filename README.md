# Razer Macro Unlocker

Use your Razer macro keys without Synapse. Keep their native F13–F24 output or
assign a shortcut, desktop, app, file, folder, or website in one Windows app.

[![Tests](https://github.com/JustAmply/razer-macro-unlocker/actions/workflows/tests.yml/badge.svg)](https://github.com/JustAmply/razer-macro-unlocker/actions/workflows/tests.yml)
[![Build and Release](https://github.com/JustAmply/razer-macro-unlocker/actions/workflows/release.yml/badge.svg)](https://github.com/JustAmply/razer-macro-unlocker/actions/workflows/release.yml)

## Get started

1. Open [Releases](https://github.com/JustAmply/razer-macro-unlocker/releases) and
   download **`RazerMacroUnlocker-App-<version>-windows-x64.zip`**.
2. Extract the entire ZIP to a permanent folder. Keep the files together.
3. Run **`RazerMacroUnlocker.exe`**. It starts the keyboard unlocker automatically.
4. Press an M key in your game's or app's keyboard-binding settings to assign it.
   By default, **M1 = F13**, **M2 = F14**, through **M5 = F17**.

The app package includes the unlocker. You do not need Python, a separate
unlocker process to start manually, or administrator rights. The self-contained
release includes the .NET runtime. Windows x64 is required.

Close Razer Synapse if it changes the keys back: Synapse can overwrite the keyboard
mode while this app is running.

## Assign your keys

On **Keys**, select an M key, choose an **Action**, set its target, and click **Save**.
Changes remain a draft until saved. Existing saved assignments stay active while
you edit.

| Action | What to choose |
| --- | --- |
| **Keyboard shortcut** | A key, optionally with Ctrl, Alt, Shift, or Win. F13–F24 are listed first. |
| **Desktop** | The position of an existing Windows virtual desktop. |
| **App or folder** | A program, file, or folder; programs can have optional arguments. |
| **Website** | A complete HTTP or HTTPS address. |

A shortcut matching a key's original signal, such as M1 → F13, passes the native
hardware event directly to the active application. Other shortcut assignments
send a single key combination. The app rejects assignments that would trigger
another configured macro action recursively.

**Test** runs an action once. It does not save the assignment. **Add key** exposes
another macro-key position for devices with more keys. It does not add physical
keys to your keyboard.

Your existing assignments are preserved when updating. The native F-key defaults
apply to a new configuration and newly added macro keys.

## Background and autostart

Open **Settings** to control the whole application:

- **Reconnect keyboard** requests a fresh hardware scan if an M key stops working.
- **Launch at login** starts the keyboard unlocker and saved assignments after you
  sign in, without opening the settings window.
- **Show tray icon** adds an optional shortcut to settings and quitting. It is off
  by default.
- **Stop background app** stops the application and releases its assignments.
- **GitHub** opens this repository for documentation, issues, and updates.

Click **Save** after changing a setting. Closing the window keeps the unlocker and
assignments running. Run `RazerMacroUnlocker.exe` again to reopen settings.

Keep the app in its permanent folder before enabling login startup. If you move
it later, open the new copy and save the startup setting again.

Settings are stored in `%LOCALAPPDATA%\Razer Macro Unlocker\settings.json`.
Configuration errors are reported without overwriting the file. To remove the
app, turn off **Launch at login**, save, stop the background app, and delete its
extracted folder. The settings file can be kept for a later installation.

## Troubleshooting

**An M key does nothing.** Close Synapse, reconnect the keyboard, and reopen the
app, then use **Settings → Reconnect keyboard**. Detection is not proof of key output: test the key in the target app's
keyboard-binding field. Some applications do not accept F13–F24.

**A desktop action fails.** Create that desktop first in Windows. Desktop numbers
follow the order in Windows' desktop overview; the app does not create or reorder
workspaces. Windows updates may require an updated desktop adapter.

**A shortcut does not reach an app.** Windows can block simulated input into an
application running at a higher privilege level. Games can also restrict it.
Release held modifier keys and test the target app's normal shortcut first.

**Will it work with anti-cheat?** Native F-key assignments use the keyboard's
hardware output. Normal operation installs no keyboard hook or custom driver and
injects no code into games. Custom shortcut actions use Windows `SendInput`.
Compatibility still depends on the game and its rules; this is not an anti-cheat
certification.

## Build from source

Install the **.NET 10 SDK** and **Python 3.15** with pip, then run on Windows x64:

```powershell
python -m pip install pyinstaller==6.22.3
./scripts/build-razer-app.ps1
./dist/RazerMacroUnlocker/RazerMacroUnlocker.exe
```

The script builds and bundles the Python unlocker with **PyInstaller 6.22.3** and
downloads the pinned, SHA-256-verified
[VirtualDesktopAccessor](https://github.com/Ciantic/VirtualDesktopAccessor) DLL.
The default local app needs the .NET 10 Desktop Runtime. To bundle it too:

```powershell
./scripts/build-razer-app.ps1 -SelfContained
```

Keep the complete `dist/RazerMacroUnlocker` folder together. No installation,
autostart change, or publication occurs during a build.

Run the checks:

```powershell
python -m unittest discover -s tests -v
dotnet run --project tests/RazerMacroUnlocker.Tests -c Release
# Optional: checks real Windows desktop state without switching desktops
dotnet run --project tests/RazerMacroUnlocker.Tests -c Release -- --integration
```

`RazerMacroUnlocker.Core` owns configuration, validation, and action dispatch.
The host owns hardware-unlocker lifetime, native hotkeys, and autostart. The
WinUI settings process communicates with it through a same-user named pipe and
exits when its window closes. Background operation is event-driven.

## Legacy command-line unlocker

The separate **`RazerMacroUnlocker.exe`** release asset is the original unlocker
without the settings UI. Use the **App ZIP** above for the complete application.
The legacy executable and `razer_unlocker.pyw` support:

| Option | Purpose |
| --- | --- |
| `--install` | Enable legacy unlocker autostart and start it. |
| `--uninstall` | Remove legacy autostart and stop it. |
| `--status` | Show service state, last scan result, and detected devices. |
| `--rescan` | Request a new device scan. |
| `--test` | Open the interactive key-output diagnostic. |
| `--help` | Show usage. |

The interactive diagnostic uses a temporary keyboard hook to display key events;
Escape exits it globally. Normal background operation does not use this hook.
The last hardware scan summary is in
`%LOCALAPPDATA%\Razer Macro Unlocker\status.txt`.

## Supported hardware

The native sequence is M1 → F13, M2 → F14, through M12 → F24, where supported by
the device. Keypads can expose the extended range. Known device IDs are listed
below; the unlocker also attempts discovery of other Razer devices. A listed ID
is not a guarantee of verification on every hardware revision.

<details>
<summary>Device IDs and native output</summary>

| Device Model | USB Product ID (PID) | Macro Key Layout | Native Output |
| :--- | :--- | :--- | :--- |
| **Razer BlackWidow Ultimate 2012** | `0x010D` | M1–M5 | `F13`–`F17` |
| **Razer BlackWidow Stealth 2012** | `0x010E` | M1–M5 | `F13`–`F17` |
| **Razer Anansi (MMO Keyboard)** | `0x010F` | M1–M5 (+ T1–T5) | `F13`–`F17` |
| **Razer Nostromo (Keypad)** | `0x0111` | Keys 01–16 | Extended Keys |
| **Razer Orbweaver (Keypad)** | `0x0113` | Keys 01–20 | Extended Keys |
| **Razer BlackWidow Ultimate 2013** | `0x011A` | M1–M5 | `F13`–`F17` |
| **Razer BlackWidow Stealth 2013/14** | `0x011B` | M1–M5 | `F13`–`F17` |
| **Razer Tartarus (Keypad)** | `0x0201` | Keys 01–15 | Extended Keys |
| **Razer BlackWidow Chroma** | `0x0203` | M1–M5 | `F13`–`F17` |
| **Razer Orbweaver Chroma** | `0x0207` | Keys 01–20 | Extended Keys |
| **Razer Tartarus Chroma** | `0x0208` | Keys 01–15 | Extended Keys |
| **Razer BlackWidow Overwatch** | `0x0211` | M1–M5 | `F13`–`F17` |
| **Razer BlackWidow Ultimate 2016** | `0x0214` | M1–M5 | `F13`–`F17` |
| **Razer BlackWidow Chroma V2** | `0x0221` | M1–M5 | `F13`–`F17` |
| **Razer BlackWidow Elite** | `0x0228` | Macro functions | `F13`–`F17` |
| **Razer Tartarus V2** | `0x022B` | Keys 01–19 | Extended Keys |
| **Razer Tartarus Pro** | `0x0244` | Keys 01–20 | Extended Keys (`F13`–`F24`) |
| **Razer BlackWidow V3** | `0x024E` | Macro functions | `F13`–`F17` |
| **Razer BlackWidow V3 Pro** | `0x0256` | Macro functions | `F13`–`F17` |
| **Razer BlackWidow V4** | `0x0287` / `0x028C` | M1–M5 | `F13`–`F17` |
| **Razer BlackWidow V4 Pro** | `0x028D` | M1–M5 + M6–M8 | `F13`–`F20` |
| **Razer BlackWidow V4 X** | `0x0293` | M1–M6 | `F13`–`F18` |
| **Razer BlackWidow V4 75%** | `0x029F` | Macro functions | Extended Keys |
| **Razer BlackWidow V4 Pro 75%** | `0x02B3` | Macro functions | Extended Keys |
| **Any Unlisted Razer Device** | `VID: 0x1532` | Automatic Detection | Dynamic Fallback (0x1F / 0x00) |

</details>
