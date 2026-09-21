"""
Universal Razer Macro Key Unlocker - Silent Background Service
Unlocks dedicated macro keys (M1-M5, M1-M8, Keypad matrices) across all supported
Razer keyboards and keypads as native F13-F17 / extended hardware keystrokes.

100% Anti-Cheat compliant: Uses standard Windows drivers (hidusb.sys).
No kernel drivers, no hooks, 0% CPU usage.
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
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]

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

user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.CreateWindowExW.restype = wintypes.HWND
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, ctypes.c_void_p
]
user32.GetMessageW.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.TranslateMessage.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.c_void_p]
user32.DispatchMessageW.restype = LRESULT
user32.DispatchMessageW.argtypes = [ctypes.c_void_p]

# Razer Device Registry with known PIDs and protocol parameters
RAZER_DEVICES = {
    # Legacy Generation Keyboards with M1-M5
    0x010D: {"name": "Razer BlackWidow Ultimate 2012", "tx_id": 0x00, "mode": 0x02},
    0x010E: {"name": "Razer BlackWidow Stealth 2012", "tx_id": 0x00, "mode": 0x02},
    0x010F: {"name": "Razer Anansi", "tx_id": 0x00, "mode": 0x02},
    0x011A: {"name": "Razer BlackWidow Ultimate 2013", "tx_id": 0x00, "mode": 0x02},
    0x011B: {"name": "Razer BlackWidow Stealth 2013/2014", "tx_id": 0x00, "mode": 0x02},
    0x0203: {"name": "Razer BlackWidow Chroma", "tx_id": 0x00, "mode": 0x02},
    0x0211: {"name": "Razer BlackWidow Overwatch", "tx_id": 0x00, "mode": 0x02},
    0x0214: {"name": "Razer BlackWidow Ultimate 2016", "tx_id": 0x00, "mode": 0x02},
    0x0221: {"name": "Razer BlackWidow Chroma V2", "tx_id": 0x00, "mode": 0x02},

    # Modern V4 Generation Keyboards with M1-M5 / M1-M8
    0x0287: {"name": "Razer BlackWidow V4", "tx_id": 0x1F, "mode": 0x02},
    0x028C: {"name": "Razer BlackWidow V4 (Alt)", "tx_id": 0x1F, "mode": 0x02},
    0x028D: {"name": "Razer BlackWidow V4 Pro", "tx_id": 0x1F, "mode": 0x02},
    0x029F: {"name": "Razer BlackWidow V4 75%", "tx_id": 0x1F, "mode": 0x02},
    0x02B3: {"name": "Razer BlackWidow V4 Pro 75%", "tx_id": 0x1F, "mode": 0x02},

    # Keypads with Macro Matrices
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
    req[0] = 0x00 # Report ID
    req[1] = 0x00 # Status
    req[2] = config["tx_id"] # Transaction ID (0x00 for legacy, 0x1F for V4)
    req[3] = 0x00 # Remaining packets MSB
    req[4] = 0x00 # Remaining packets LSB
    req[5] = 0x00 # Protocol type
    req[6] = 0x02 # Data size
    req[7] = 0x00 # Command Class
    req[8] = 0x04 # Command ID: Set Device Mode
    req[9] = config["mode"] # Mode (0x02 = Legacy / Macro Key Mode)
    req[10] = 0x00 # Param
    req[89] = calc_crc(req)
    req[90] = 0x00 # Reserved

    buf = (ctypes.c_byte * 91).from_buffer(req)
    ok = hid.HidD_SetFeature(h, buf, 91)
    kernel32.CloseHandle(h)
    return ok

def unlock_all_keyboards():
    devices = find_all_razer_ctrl_devices()
    unlocked = 0
    for path, pid in devices:
        if unlock_device(path, pid):
            unlocked += 1
    return unlocked > 0

WM_DEVICECHANGE = 0x0219
WM_POWERBROADCAST = 0x0218
PBT_APMRESUMEAUTOMATIC = 0x0012
PBT_APMRESUMESUSPEND = 0x0007

WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, WPARAM, LPARAM)

class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ('style', wintypes.UINT), ('lpfnWndProc', WNDPROC),
        ('cbClsExtra', ctypes.c_int), ('cbWndExtra', ctypes.c_int),
        ('hInstance', wintypes.HINSTANCE), ('hIcon', wintypes.HICON),
        ('hCursor', wintypes.HICON), ('hbrBackground', wintypes.HBRUSH),
        ('lpszMenuName', wintypes.LPCWSTR), ('lpszClassName', wintypes.LPCWSTR)
    ]

def wnd_proc(hwnd, msg, wparam, lparam):
    # Re-unlock keyboards on device reconnect or standby wake-up
    if msg == WM_DEVICECHANGE or (msg == WM_POWERBROADCAST and wparam in (PBT_APMRESUMEAUTOMATIC, PBT_APMRESUMESUSPEND)):
        time.sleep(1.0) # Small delay to allow USB enumeration to complete
        unlock_all_keyboards()
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

def main():
    # Attempt unlock on startup (retry up to 5 times)
    for _ in range(5):
        if unlock_all_keyboards():
            break
        time.sleep(2.0)

    # Register hidden message-only window to receive USB and Power events
    wnd_proc_cb = WNDPROC(wnd_proc)
    wnd_class = WNDCLASSW()
    wnd_class.lpfnWndProc = wnd_proc_cb
    wnd_class.lpszClassName = "RazerUnlockerServiceClass"
    wnd_class.hInstance = kernel32.GetModuleHandleW(None)
    user32.RegisterClassW(ctypes.byref(wnd_class))

    hwnd = user32.CreateWindowExW(0, "RazerUnlockerServiceClass", "RazerUnlocker", 0, 0, 0, 0, 0, None, None, wnd_class.hInstance, None)

    # Passive message loop (0% CPU usage)
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

if __name__ == '__main__':
    main()
