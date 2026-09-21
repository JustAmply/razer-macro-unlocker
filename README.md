# Universal Razer Macro Key Unlocker (M1–M5 to F13–F17)

A lightweight, silent Windows background service that automatically unlocks dedicated macro keys (**M1–M5**, **M1–M8**, and **Keypad matrices**) across **all Razer keyboards and keypads** as native **F13–F17** hardware keystrokes.

**100% Anti-Cheat compliant, zero drivers, and completely free of Razer Synapse!**

---

## Key Highlights

- **100% Anti-Cheat Safe:** Uses exclusively the standard Windows USB HID driver (`hidusb.sys`). No kernel-level drivers, no Interception driver, no DLL injection, and no background keyboard hooks.
- **Genuine Hardware Signals:** By sending a standard USB HID Feature Report to switch the keyboard into Legacy Mode, the keyboard's internal controller emits native hardware scancodes for `F13` through `F17`.
- **Universal Multi-Device Support:** Automatically enumerates all connected Razer keyboards and keypads, unlocks each device dynamically, and responds to USB reconnects and standby wakeups.
- **0% CPU & Minimal RAM:** Unlocks the hardware upon startup/reconnect and remains passive in the background.
- **Instant Game Integration:** Any game, Discord, OBS, or voice chat tool immediately recognizes M1–M5 directly as independent function keys `F13`–`F17` in keybinding menus.

---

## Supported Devices Matrix

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
| **Razer Tartarus V2** | `0x022B` | Keys 01–19 | Extended Keys |
| **Razer BlackWidow V4** | `0x0287` / `0x028C` | M1–M5 | `F13`–`F17` |
| **Razer BlackWidow V4 Pro** | `0x028D` | M1–M5 + M6–M8 | `F13`–`F17` + Extended |
| **Razer BlackWidow V4 75%** | `0x029F` | Macro functions | Extended Keys |
| **Razer BlackWidow V4 Pro 75%** | `0x02B3` | Macro functions | Extended Keys |
| **Any Unlisted Razer Device** | `VID: 0x1532` | Automatic Detection | Safe Mode 0x02 Fallback |

---

## Key Mapping (M1–M5)

| Physical Key | Virtual-Key Code | Windows Virtual Key | Hardware ScanCode |
| :--- | :--- | :--- | :--- |
| **M1** | `0x7C` (124) | **`F13`** | `0x64` |
| **M2** | `0x7D` (125) | **`F14`** | `0x65` |
| **M3** | `0x7E` (126) | **`F15`** | `0x66` |
| **M4** | `0x7F` (127) | **`F16`** | `0x67` |
| **M5** | `0x80` (128) | **`F17`** | `0x68` |

## Download & Quick Start (No Python Required!)

For standard users and gamers, **no Python installation is required**:

1. **Download:** Go to the [Releases](https://github.com/JustAmply/razer-macro-unlocker/releases) page and download **`RazerMacroUnlocker.exe`** (or the complete **`RazerMacroUnlocker-windows-x64.zip`** bundle).
2. **Instant Run:** Simply launch **`RazerMacroUnlocker.exe`**. It will unlock all connected Razer keyboards and keypads immediately and run silently in the background with 0% CPU.
3. **Autostart with Windows:**
   - Run `RazerMacroUnlocker.exe --install` in your terminal or Command Prompt.
   - It automatically creates a shortcut in your Windows Startup folder (`shell:startup`) and launches the service.

---

## Command-Line Interface (CLI)

`RazerMacroUnlocker.exe` (and `razer_unlocker.pyw`) supports built-in command-line arguments:

```powershell
# Configure autostart with Windows and launch background service
.\RazerMacroUnlocker.exe --install

# Remove autostart shortcut and terminate running background services
.\RazerMacroUnlocker.exe --uninstall

# Run interactive diagnostic test and live keystroke monitor
.\RazerMacroUnlocker.exe --test

# List all detected Razer control devices and their status
.\RazerMacroUnlocker.exe --status

# Send an immediate re-scan and unlock signal to the running background service
.\RazerMacroUnlocker.exe --rescan

# Display help message
.\RazerMacroUnlocker.exe --help
```

---

## Installation & Usage (From Source)

If you prefer to run from source or build the executable yourself:

### Option A: Run directly with Python
1. Ensure Python 3.10+ is installed.
2. Run `python razer_unlocker.pyw --install` to configure autostart and launch the service.

### Option B: Build Standalone .exe Locally
1. Run **`build_exe.bat`**.
2. PyInstaller will compile `razer_unlocker.pyw` into a portable `dist\RazerMacroUnlocker.exe`.

---

## Uninstallation

- Run `RazerMacroUnlocker.exe --uninstall` (or `python razer_unlocker.pyw --uninstall`) to remove the autostart shortcut and terminate all running background instances.

---

## Live Diagnostic & Testing

- Run `RazerMacroUnlocker.exe --test` (or `python razer_unlocker.pyw --test`) to open an interactive console window that detects all connected Razer devices, unlocks them, and displays incoming keystrokes in real time.

