# Razer BlackWidow Chroma V2 – Macro Key Unlocker (M1–M5 to F13–F17)

Ein leichtgewichtiger, geräuschloser Windows-Hintergrunddienst zur Freischaltung der dedizierten Makrotasten (M1–M5) einer **Razer BlackWidow Chroma V2** (`VID: 0x1532`, `PID: 0x0221`) als native **F13–F17** Hardware-Tastendrücke.

**Vollständig ohne Razer Synapse und ohne Anti-Cheat-Treiber!**

---

## Highlights

- **100 % Anti-Cheat-sicher:** Verwendet ausschließlich die Standard-Windows-HID-Treiber (`hidusb.sys`). Keine Kernel-Treiber, kein Interception-Treiber, keine DLL-Injection und kein Hooking.
- **Echte Hardware-Signale:** Die Tastatur-Firmware wird über einen USB-HID-Feature-Report in den Legacy-Modus versetzt und sendet daraufhin native Hardware-Scancodes für `F13` bis `F17`.
- **0 % CPU & minimaler RAM:** Der Dienst schaltet die Tastatur beim Start frei und wartet ansonsten passiv im Hintergrund auf USB-Reconnects und Standby-Wakeups.
- **Sofort in Spielen nutzbar:** Jedes Spiel (und Tools wie Discord, OBS, TeamSpeak) erkennt M1–M5 direkt als eigenständige Funktionstasten `F13` bis `F17`.

---

## Tastenbelegung

| Taste auf der Tastatur | Virtual-Key Code | Windows-Taste | Hardware-ScanCode |
| :--- | :--- | :--- | :--- |
| **M1** | `0x7C` (124) | **`F13`** | `0x64` |
| **M2** | `0x7D` (125) | **`F14`** | `0x65` |
| **M3** | `0x7E` (126) | **`F15`** | `0x66` |
| **M4** | `0x7F` (127) | **`F16`** | `0x67` |
| **M5** | `0x80` (128) | **`F17`** | `0x68` |

---

## Installation

1. Führe **`install_autostart.bat`** aus.
2. Das Skript richtet automatisch eine Verknüpfung in deinem Windows-Autostart-Ordner (`shell:startup`) ein und startet den Dienst geräuschlos im Hintergrund.

---

## Deinstallation

- Führe **`uninstall_autostart.bat`** aus, um die Autostart-Verknüpfung zu entfernen und laufende Instanzen zu beenden.

---

## Live-Test & Diagnose

- Führe **`run_test.bat`** aus, um ein Konsolenfenster zu öffnen, das alle Tastendrücke in Echtzeit anzeigt.
