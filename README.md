# Universal Razer Macro Key Unlocker

Unlock dedicated Razer macro keys (**M1–M5**, **M1–M8**, and **Keypad matrices**) across Razer keyboards and keypads as native **F13–F24** hardware keystrokes — completely independent of Razer Synapse.

[![Build and Release](https://github.com/JustAmply/razer-macro-unlocker/actions/workflows/release.yml/badge.svg)](https://github.com/JustAmply/razer-macro-unlocker/actions/workflows/release.yml)

---

## Table of Contents

- [Key Highlights](#key-highlights)
- [Why F13–F24?](#why-f13f24)
- [Download & Quick Start](#download--quick-start)
- [Command-Line Interface (CLI)](#command-line-interface-cli)
- [Key Mapping](#key-mapping)
- [Supported Devices](#supported-devices)
- [Running from Source & Building](#running-from-source--building)
- [How It Works & Anti-Cheat Safety](#how-it-works--anti-cheat-safety)

---

## Key Highlights

- **Anti-Cheat Safe:** Uses exclusively the standard Windows USB HID driver (`hidusb.sys`). No kernel drivers, no Interception drivers, and no DLL injection.
- **Genuine Hardware Signals:** Switches the keyboard controller into Legacy Mode via a standard USB HID Feature Report, causing the keyboard to emit native hardware scancodes.
- **Background Reliability:** Automatically detects connected Razer keyboards and keypads, with re-unlock on USB reconnect and system sleep/wake.
- **0% CPU Usage:** Remains completely idle in the background once devices are unlocked.
- **Synapse-Free:** No Razer Synapse installation or background telemetry required.

---

## Why F13–F24?

Standard PC keyboards only feature physical function keys from **F1** to **F12**. However, Windows natively defines Virtual-Key codes up to **F24** (`0x7C` through `0x87`).

- **No Conflicts:** F13–F24 keys never interfere with your regular keyboard typing, numpad, or navigation keys.
- **Native Recognition:** Games, Discord, OBS Studio, and voice chat applications immediately recognize F13–F24 as independent keys in their keybinding settings.

---

## Download & Quick Start

For standard users, **no Python installation is required**:

1. **Download:** Go to the [Releases](https://github.com/JustAmply/razer-macro-unlocker/releases) page and download **`RazerMacroUnlocker.exe`** (or the complete **`RazerMacroUnlocker-windows-x64.zip`** bundle).
2. **Run Once:** Launch `RazerMacroUnlocker.exe`. It unlocks all connected Razer keyboards immediately and runs silently in the background.
3. **Autostart with Windows (Optional):**
   - Double-click **`install_autostart.bat`** (or run `RazerMacroUnlocker.exe --install` in a terminal).
   - This registers the application in the Windows Registry (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`) and starts the service.

> [!IMPORTANT]
> **Razer Synapse Interaction:**
> If Razer Synapse is running at the same time, it may overwrite the keyboard mode. It is recommended to close or disable the autostart of Razer Synapse to avoid mode conflicts.

> [!TIP]
> **Keybinding in Games & Discord:**
> In any game, Discord, or OBS keybinding menu, simply press your physical **M1–M5** key when prompted — it will register directly as **F13–F17**.

---

## Command-Line Interface (CLI)

`RazerMacroUnlocker.exe` (and `razer_unlocker.pyw`) supports built-in command-line arguments:

```powershell
# Configure autostart with Windows and start background service
.\RazerMacroUnlocker.exe --install   # (or -i)

# Remove autostart entry and stop running background service
.\RazerMacroUnlocker.exe --uninstall # (or -u)

# Run interactive diagnostic test and live keystroke monitor
.\RazerMacroUnlocker.exe --test      # (or -t)

# List detected Razer control devices and their status
.\RazerMacroUnlocker.exe --status    # (or -s)

# Send an immediate re-scan signal to the running background service
.\RazerMacroUnlocker.exe --rescan    # (or -r)

# Display help message
.\RazerMacroUnlocker.exe --help      # (or -h)
```

`--status` shows whether the background service is running, whether autostart is configured,
the last scan result, and detected control devices. Detection alone does not prove that
the macro keys are unlocked. Use `--test` and press a macro key to verify its F13–F24 output.
`--rescan` returns a successful exit code when its request reaches the running service;
the last scan result appears under `--status` after the service processes it. Without a
running service, `--rescan` attempts to unlock directly and reports failure with exit code 1.
Invalid options return exit code 2. The interactive test's Escape key is global while
the listener is active, so it works even when another window has focus.

---

## Key Mapping

| Physical Key | Virtual-Key Code | Windows Virtual Key | Hardware ScanCode |
| :--- | :--- | :--- | :--- |
| **M1** | `0x7C` (124) | **`F13`** | `0x64` |
| **M2** | `0x7D` (125) | **`F14`** | `0x65` |
| **M3** | `0x7E` (126) | **`F15`** | `0x66` |
| **M4** | `0x7F` (127) | **`F16`** | `0x67` |
| **M5** | `0x80` (128) | **`F17`** | `0x68` |
| **M6 / Keypad** | `0x81` (129) | **`F18`** | `0x69` |
| **M7 / Keypad** | `0x82` (130) | **`F19`** | `0x6A` |
| **M8 / Keypad** | `0x83` (131) | **`F20`** | `0x6B` |
| **Keypad** | `0x84` (132) | **`F21`** | `0x6C` |
| **Keypad** | `0x85` (133) | **`F22`** | `0x6D` |
| **Keypad** | `0x86` (134) | **`F23`** | `0x6E` |
| **Keypad** | `0x87` (135) | **`F24`** | `0x6F` |

---

## Supported Devices

All Razer devices share Vendor ID `0x1532`. Unlisted Razer keyboards are dynamically detected and supported through an automatic fallback mechanism.

<details>
<summary><b>Click to expand the list of tested devices (25+ models)</b></summary>

<br>

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

---

## Running from Source & Building

### Option A: Run directly with Python
1. Ensure Python 3.10+ is installed.
2. Launch the script directly:
   ```powershell
   # Run in background
   python razer_unlocker.pyw

   # Or configure autostart
   python razer_unlocker.pyw --install
   ```
   *(Note: The `.bat` helper scripts are intended for `RazerMacroUnlocker.exe`.)*

### Option B: Build Standalone .exe Locally
1. Run **`build_exe.bat`** (requires Python with `pip` or `uv`).
2. PyInstaller compiles `razer_unlocker.pyw` into `dist\RazerMacroUnlocker.exe`.

---

## Live Diagnostic & Testing

To test device detection and see your keystrokes live:
- Run **`run_test.bat`** (or execute `RazerMacroUnlocker.exe --test` / `python razer_unlocker.pyw --test`).
- An interactive console opens, lists detected devices, unlocks them, and logs all incoming keystrokes in real time. Press `Escape` to close the test.

The background service writes its latest scan summary to
`%LOCALAPPDATA%\RazerMacroUnlocker\status.txt`. This reports whether an HID feature report
was accepted; the interactive key test is still needed to confirm actual key output.

---

## How It Works & Anti-Cheat Safety

1. **Device Enumeration:** The tool queries Windows HID device interfaces to locate connected devices matching Razer's Vendor ID (`0x1532`) that feature a 91-byte control endpoint.
2. **Feature Report:** It sends a standard HID Feature Report (`HidD_SetFeature`) requesting Mode `0x02` (Legacy Mode).
3. **Hardware Keystrokes:** The keyboard microcontroller begins sending hardware scancodes for `F13` through `F17` directly over USB.
4. **Passive Monitoring:** A hidden window listens for Windows system messages (`WM_DEVICECHANGE`, `WM_POWERBROADCAST`, and `WM_WTSSESSION_CHANGE`) to re-unlock devices automatically upon reconnect or wake-up.

> [!NOTE]
> **Anti-Cheat Clarification:**
> In normal background service mode, the application **never** installs keyboard hooks (`SetWindowsHookEx`) or intercepts keystrokes. Input goes directly from the Windows HID driver into your active application or game. A temporary low-level keyboard hook is used **only** while running the interactive diagnostic test (`--test`) to print key codes to the console.

---

## Uninstallation

- Run **`uninstall_autostart.bat`** (or `RazerMacroUnlocker.exe --uninstall`).
- This removes the Windows Registry autostart entry and terminates any running background service instances.
