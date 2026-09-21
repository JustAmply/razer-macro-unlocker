import ctypes
from ctypes import wintypes
import time
import sys

kernel32 = ctypes.WinDLL('kernel32.dll')
user32 = ctypes.WinDLL('user32.dll')
hid = ctypes.WinDLL('hid.dll')

LRESULT = ctypes.c_longlong
WPARAM = ctypes.c_ulonglong
LPARAM = ctypes.c_longlong

kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

hid.HidD_SetFeature.restype = wintypes.BOOL
hid.HidD_SetFeature.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.ULONG]
hid.HidD_GetFeature.restype = wintypes.BOOL
hid.HidD_GetFeature.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.ULONG]

user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.CallNextHookEx.restype = LRESULT
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, WPARAM, LPARAM]
user32.GetMessageW.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.TranslateMessage.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.c_void_p]
user32.DispatchMessageW.restype = LRESULT
user32.DispatchMessageW.argtypes = [ctypes.c_void_p]
user32.PostQuitMessage.restype = None
user32.PostQuitMessage.argtypes = [ctypes.c_int]

def calc_crc(buf):
    crc = 0
    for b in buf[3:89]:
        crc ^= b
    return crc

def set_legacy_mode():
    path = r'\\?\hid#vid_1532&pid_0221&mi_02#a&b377700&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
    h = kernel32.CreateFileW(path, 0, 3, None, 3, 0, None)
    if h == -1 or h == 0 or h == 0xFFFFFFFFFFFFFFFF:
        print("FEHLER: Konnte Steuer-Schnittstelle nicht öffnen.")
        return False

    req = bytearray(91)
    req[0] = 0x00 # Report ID
    req[1] = 0x00 # Status
    req[2] = 0x00 # Transaction ID = 0x00
    req[3] = 0x00 # Remaining packets MSB
    req[4] = 0x00 # Remaining packets LSB
    req[5] = 0x00 # Protocol type
    req[6] = 0x02 # Data size
    req[7] = 0x00 # Command Class
    req[8] = 0x04 # Command ID: Set Device Mode
    req[9] = 0x02 # Mode 0x02 = Legacy / Macro Key Mode (M1-M5 -> F13-F17)
    req[10] = 0x00 # Param
    req[89] = calc_crc(req)
    req[90] = 0x00 # Reserved

    buf = (ctypes.c_byte * 91).from_buffer(req)
    ok = hid.HidD_SetFeature(h, buf, 91)
    
    resp = (ctypes.c_byte * 91)()
    resp[0] = 0x00
    hid.HidD_GetFeature(h, resp, 91)
    kernel32.CloseHandle(h)

    status = resp[1]
    print(f"Legacy-Modus gesendet. Ergebnis: {'OK (0x02)' if status == 0x02 else f'Status 0x{status:02X}'}")
    return ok and (status == 0x02)

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ('vkCode', wintypes.DWORD),
        ('scanCode', wintypes.DWORD),
        ('flags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_ulonglong)
    ]

HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)

M_KEYS = {
    0x7C: ("M1", "F13"),
    0x7D: ("M2", "F14"),
    0x7E: ("M3", "F15"),
    0x7F: ("M4", "F16"),
    0x80: ("M5", "F17")
}

def main():
    print("========================================================")
    print("       Razer BlackWidow Chroma V2 - Live Test          ")
    print("========================================================")
    
    if not set_legacy_mode():
        input("\nFehler beim Freischalten. Drücke Enter...")
        return

    print("\nTastatur ist im Legacy-Modus (M1-M5 senden F13-F17)!")
    print("Der Live-Listener ist aktiv.")
    print("Bitte drücke die Tasten M1 bis M5 oder normale Tasten.")
    print("Zum Beenden drücke ESCAPE im Konsolenfenster.\n")

    def hook_callback(nCode, wParam, lParam):
        if nCode >= 0:
            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            state = "DOWN" if wParam in (0x0100, 0x0104) else "UP"

            if kb.vkCode in M_KEYS:
                m_label, f_key = M_KEYS[kb.vkCode]
                print(f"  >>> [MAKROTASTE] {m_label} -> Windows erkennt {f_key} ({state}) | VK=0x{kb.vkCode:02X}, ScanCode=0x{kb.scanCode:02X}")
            else:
                print(f"  Taste: {state} | VK=0x{kb.vkCode:02X} (Dec: {kb.vkCode}), ScanCode=0x{kb.scanCode:02X}")

            if kb.vkCode == 0x1B: # Escape
                print("\nEscape gedrückt - beende...")
                user32.PostQuitMessage(0)

        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    cb = HOOKPROC(hook_callback)
    h_hook = user32.SetWindowsHookExW(13, cb, None, 0)
    if not h_hook:
        print("Fehler beim Hook-Setup:", kernel32.GetLastError())
        input("\nDrücke Enter...")
        return

    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    user32.UnhookWindowsHookEx(h_hook)
    print("Test erfolgreich beendet.")

if __name__ == '__main__':
    main()
