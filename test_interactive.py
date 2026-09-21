"""
Interactive diagnostic and test utility for Razer Keyboards & Keypads.
Detects all connected Razer devices, unlocks them, and displays incoming keystrokes.
"""

import ctypes
from ctypes import wintypes
import re
import time
import sys

kernel32 = ctypes.WinDLL('kernel32.dll')
user32 = ctypes.WinDLL('user32.dll')
hid = ctypes.WinDLL('hid.dll')
setupapi = ctypes.WinDLL('setupapi.dll')

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
hid.HidD_GetPreparsedData.restype = wintypes.BOOL
hid.HidD_GetPreparsedData.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p)]
hid.HidD_FreePreparsedData.restype = wintypes.BOOL
hid.HidD_FreePreparsedData.argtypes = [ctypes.c_void_p]

class GUID(ctypes.Structure):
    _fields_ = [('Data1', wintypes.DWORD), ('Data2', wintypes.WORD), ('Data3', wintypes.WORD), ('Data4', wintypes.BYTE * 8)]

class DID(ctypes.Structure):
    _fields_ = [('cbSize', wintypes.DWORD), ('guid', GUID), ('flags', wintypes.DWORD), ('reserved', ctypes.c_size_t)]

class HIDP_CAPS(ctypes.Structure):
    _fields_ = [
        ('Usage', wintypes.USHORT), ('UsagePage', wintypes.USHORT),
        ('InputReportByteLength', wintypes.USHORT), ('OutputReportByteLength', wintypes.USHORT),
        ('FeatureReportByteLength', wintypes.USHORT), ('Reserved', wintypes.USHORT * 17),
        ('NumberLinkCollectionNodes', wintypes.USHORT),
        ('NumberInputButtonCaps', wintypes.USHORT),
        ('NumberInputValueCaps', wintypes.USHORT),
        ('NumberInputDataIndices', wintypes.USHORT),
        ('NumberOutputButtonCaps', wintypes.USHORT),
        ('NumberOutputValueCaps', wintypes.USHORT),
        ('NumberOutputDataIndices', wintypes.USHORT),
        ('NumberFeatureButtonCaps', wintypes.USHORT),
        ('NumberFeatureValueCaps', wintypes.USHORT),
        ('NumberFeatureDataIndices', wintypes.USHORT),
    ]

hid.HidP_GetCaps.restype = wintypes.LONG
hid.HidP_GetCaps.argtypes = [ctypes.c_void_p, ctypes.POINTER(HIDP_CAPS)]

setupapi.SetupDiGetClassDevsW.restype = wintypes.HANDLE
setupapi.SetupDiGetClassDevsW.argtypes = [ctypes.POINTER(GUID), wintypes.LPCWSTR, wintypes.HWND, wintypes.DWORD]
setupapi.SetupDiEnumDeviceInterfaces.restype = wintypes.BOOL
setupapi.SetupDiEnumDeviceInterfaces.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(GUID), wintypes.DWORD, ctypes.POINTER(DID)]
setupapi.SetupDiGetDeviceInterfaceDetailW.restype = wintypes.BOOL
setupapi.SetupDiGetDeviceInterfaceDetailW.argtypes = [wintypes.HANDLE, ctypes.POINTER(DID), ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
setupapi.SetupDiDestroyDeviceInfoList.restype = wintypes.BOOL
setupapi.SetupDiDestroyDeviceInfoList.argtypes = [wintypes.HANDLE]

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

RAZER_DEVICES = {
    0x010D: {"name": "Razer BlackWidow Ultimate 2012", "tx_id": 0x00, "mode": 0x02},
    0x010E: {"name": "Razer BlackWidow Stealth 2012", "tx_id": 0x00, "mode": 0x02},
    0x010F: {"name": "Razer Anansi", "tx_id": 0x00, "mode": 0x02},
    0x011A: {"name": "Razer BlackWidow Ultimate 2013", "tx_id": 0x00, "mode": 0x02},
    0x011B: {"name": "Razer BlackWidow Stealth 2013/2014", "tx_id": 0x00, "mode": 0x02},
    0x0203: {"name": "Razer BlackWidow Chroma", "tx_id": 0x00, "mode": 0x02},
    0x0211: {"name": "Razer BlackWidow Overwatch", "tx_id": 0x00, "mode": 0x02},
    0x0214: {"name": "Razer BlackWidow Ultimate 2016", "tx_id": 0x00, "mode": 0x02},
    0x0221: {"name": "Razer BlackWidow Chroma V2", "tx_id": 0x00, "mode": 0x02},

    0x0287: {"name": "Razer BlackWidow V4", "tx_id": 0x1F, "mode": 0x02},
    0x028C: {"name": "Razer BlackWidow V4 (Alt)", "tx_id": 0x1F, "mode": 0x02},
    0x028D: {"name": "Razer BlackWidow V4 Pro", "tx_id": 0x1F, "mode": 0x02},
    0x029F: {"name": "Razer BlackWidow V4 75%", "tx_id": 0x1F, "mode": 0x02},
    0x02B3: {"name": "Razer BlackWidow V4 Pro 75%", "tx_id": 0x1F, "mode": 0x02},

    0x0111: {"name": "Razer Nostromo", "tx_id": 0x00, "mode": 0x02},
    0x0113: {"name": "Razer Orbweaver", "tx_id": 0x00, "mode": 0x02},
    0x0201: {"name": "Razer Tartarus", "tx_id": 0x00, "mode": 0x02},
    0x0207: {"name": "Razer Orbweaver Chroma", "tx_id": 0x00, "mode": 0x02},
    0x0208: {"name": "Razer Tartarus Chroma", "tx_id": 0x00, "mode": 0x02},
    0x022B: {"name": "Razer Tartarus V2", "tx_id": 0x00, "mode": 0x02},
}

def calc_crc(buf):
    crc = 0
    for b in buf[3:89]:
        crc ^= b
    return crc

def find_all_razer_ctrl_devices():
    guid = GUID()
    hid.HidD_GetHidGuid(ctypes.byref(guid))
    hdev = setupapi.SetupDiGetClassDevsW(ctypes.byref(guid), None, None, 0x12)

    did = DID()
    did.cbSize = ctypes.sizeof(DID)
    index = 0
    devices = []

    while setupapi.SetupDiEnumDeviceInterfaces(hdev, None, ctypes.byref(guid), index, ctypes.byref(did)):
        index += 1
        req = wintypes.DWORD()
        setupapi.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(did), None, 0, ctypes.byref(req), None)
        buf = (ctypes.c_byte * req.value)()
        cbSize = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
        ctypes.cast(buf, ctypes.POINTER(wintypes.DWORD))[0] = cbSize
        if setupapi.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(did), buf, req.value, None, None):
            path = ctypes.wstring_at(ctypes.addressof(buf) + 4)
            if 'vid_1532' in path.lower():
                h = kernel32.CreateFileW(path, 0, 3, None, 3, 0, None)
                if h != -1 and h != 0 and h != 0xFFFFFFFFFFFFFFFF:
                    preparsed = ctypes.c_void_p()
                    if hid.HidD_GetPreparsedData(h, ctypes.byref(preparsed)):
                        caps = HIDP_CAPS()
                        hid.HidP_GetCaps(preparsed, ctypes.byref(caps))
                        hid.HidD_FreePreparsedData(preparsed)
                        kernel32.CloseHandle(h)
                        if caps.FeatureReportByteLength == 91:
                            m = re.search(r'pid_([0-9a-fA-F]{4})', path, re.IGNORECASE)
                            pid = int(m.group(1), 16) if m else 0
                            devices.append((path, pid))
                    else:
                        kernel32.CloseHandle(h)

    setupapi.SetupDiDestroyDeviceInfoList(hdev)
    return devices

def unlock_device(path, pid):
    config = RAZER_DEVICES.get(pid, {"name": f"Unknown Razer Device (PID: 0x{pid:04X})", "tx_id": 0x00, "mode": 0x02})

    h = kernel32.CreateFileW(path, 0, 3, None, 3, 0, None)
    if h == -1 or h == 0 or h == 0xFFFFFFFFFFFFFFFF:
        return False

    req = bytearray(91)
    req[0] = 0x00
    req[1] = 0x00
    req[2] = config["tx_id"]
    req[3] = 0x00
    req[4] = 0x00
    req[5] = 0x00
    req[6] = 0x02
    req[7] = 0x00
    req[8] = 0x04
    req[9] = config["mode"]
    req[10] = 0x00
    req[89] = calc_crc(req)
    req[90] = 0x00

    buf = (ctypes.c_byte * 91).from_buffer(req)
    ok = hid.HidD_SetFeature(h, buf, 91)
    kernel32.CloseHandle(h)
    return ok

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
    print("       Universal Razer Macro Key Unlocker - Test        ")
    print("========================================================")
    
    devices = find_all_razer_ctrl_devices()
    if not devices:
        print("ERROR: No Razer devices found with 91-byte control endpoints.")
        input("\nPress Enter to exit...")
        return

    print(f"Found {len(devices)} Razer control device(s):")
    for path, pid in devices:
        name = RAZER_DEVICES.get(pid, {}).get("name", f"Unknown Razer Device (PID: 0x{pid:04X})")
        ok = unlock_device(path, pid)
        status_str = "SUCCESS" if ok else "FAILED"
        print(f"  - [{status_str}] {name} (PID: 0x{pid:04X})")

    print("\nLive key listener is active.")
    print("Press M1 to M5 or any standard keys.")
    print("To exit, press ESCAPE in this console window.\n")

    def hook_callback(nCode, wParam, lParam):
        if nCode >= 0:
            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            state = "DOWN" if wParam in (0x0100, 0x0104) else "UP"

            if kb.vkCode in M_KEYS:
                m_label, f_key = M_KEYS[kb.vkCode]
                print(f"  >>> [MACRO KEY] {m_label} -> Windows detects {f_key} ({state}) | VK=0x{kb.vkCode:02X}, ScanCode=0x{kb.scanCode:02X}")
            else:
                print(f"  Key: {state} | VK=0x{kb.vkCode:02X} (Dec: {kb.vkCode}), ScanCode=0x{kb.scanCode:02X}")

            if kb.vkCode == 0x1B: # Escape
                print("\nEscape pressed - exiting...")
                user32.PostQuitMessage(0)

        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    cb = HOOKPROC(hook_callback)
    h_hook = user32.SetWindowsHookExW(13, cb, None, 0)
    if not h_hook:
        print("Hook setup error:", kernel32.GetLastError())
        input("\nPress Enter to exit...")
        return

    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    user32.UnhookWindowsHookEx(h_hook)
    print("Test completed successfully.")

if __name__ == '__main__':
    main()
