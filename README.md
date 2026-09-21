# Razer BlackWidow Chroma V2 – Macro Key Unlocker (M1–M5 to F13–F17)

A lightweight, silent Windows background service that unlocks the dedicated macro keys (M1–M5) on the **Razer BlackWidow Chroma V2** (`VID: 0x1532`, `PID: 0x0221`) as native **F13–F17** hardware keystrokes.

**Completely free of Razer Synapse and 100% Anti-Cheat compliant!**

---

## Key Highlights

- **100% Anti-Cheat Safe:** Uses exclusively standard Windows HID drivers (`hidusb.sys`). No kernel drivers, no Interception driver, no DLL injection, and no keyboard hooking in the background service.
- **Genuine Hardware Signals:** By sending a standard USB HID Feature Report to switch the keyboard into Legacy Mode, the keyboard's onboard controller emits native hardware scancodes for `F13` through `F17`.
- **0% CPU & Minimal RAM:** The service unlocks the keyboard upon startup and waits passively in the background for USB reconnects and standby wakeups.
- **Instantly Usable in Games & Apps:** Any game (as well as Discord, OBS, TeamSpeak, etc.) immediately recognizes M1–M5 as independent function keys `F13`–`F17` when binding keys in the settings menu.

---

## Key Mapping

| Keyboard Key | Virtual-Key Code | Windows Key | Hardware ScanCode |
| :--- | :--- | :--- | :--- |
| **M1** | `0x7C` (124) | **`F13`** | `0x64` |
| **M2** | `0x7D` (125) | **`F14`** | `0x65` |
| **M3** | `0x7E` (126) | **`F15`** | `0x66` |
| **M4** | `0x7F` (127) | **`F16`** | `0x67` |
| **M5** | `0x80` (128) | **`F17`** | `0x68` |

---

## Installation

1. Run **`install_autostart.bat`**.
2. The script creates a shortcut in your Windows Startup directory (`shell:startup`) and starts the service silently in the background.

---

## Uninstallation

- Run **`uninstall_autostart.bat`** to remove the startup shortcut and terminate any running background instances.

---

## Live Diagnostic & Testing

- Run **`run_test.bat`** to open an interactive console window that displays all incoming key events in real time.
