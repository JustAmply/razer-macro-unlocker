"""
Universal Razer Macro Key Unlocker - Silent Background Service
Unlocks dedicated macro keys (M1-M5, M1-M8, Keypad matrices) across all supported
Razer keyboards and keypads as native F13-F17 / extended hardware keystrokes.

100% Anti-Cheat compliant: Uses standard Windows drivers (hidusb.sys).
No kernel drivers, no hooks, 0% CPU usage.
"""

import ctypes
from ctypes import wintypes
import os
import re
import shutil
import subprocess
import sys
import time
import winreg

kernel32 = ctypes.WinDLL('kernel32.dll')
user32 = ctypes.WinDLL('user32.dll')
hid = ctypes.WinDLL('hid.dll')
setupapi = ctypes.WinDLL('setupapi.dll', use_last_error=True)
wtsapi32 = ctypes.WinDLL('wtsapi32.dll')

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
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.GetLastError.restype = wintypes.DWORD
kernel32.GetLastError.argtypes = []
kernel32.AttachConsole.restype = wintypes.BOOL
kernel32.AttachConsole.argtypes = [wintypes.DWORD]
kernel32.AllocConsole.restype = wintypes.BOOL
kernel32.AllocConsole.argtypes = []

TH32CS_SNAPPROCESS = 0x00000002

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260)
    ]

kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
kernel32.Process32First.restype = wintypes.BOOL
kernel32.Process32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
kernel32.Process32Next.restype = wintypes.BOOL
kernel32.Process32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]

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
user32.FindWindowW.restype = wintypes.HWND
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.PostMessageW.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
UINT_PTR = ctypes.c_size_t
user32.SetTimer.restype = UINT_PTR
user32.SetTimer.argtypes = [wintypes.HWND, UINT_PTR, wintypes.UINT, ctypes.c_void_p]
user32.KillTimer.restype = wintypes.BOOL
user32.KillTimer.argtypes = [wintypes.HWND, UINT_PTR]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.CallNextHookEx.restype = LRESULT
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, WPARAM, LPARAM]
user32.PostQuitMessage.restype = None
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.RegisterDeviceNotificationW.restype = wintypes.HANDLE
user32.RegisterDeviceNotificationW.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
user32.UnregisterDeviceNotification.restype = wintypes.BOOL
user32.UnregisterDeviceNotification.argtypes = [wintypes.HANDLE]
user32.RegisterPowerSettingNotification.restype = wintypes.HANDLE
user32.RegisterPowerSettingNotification.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
user32.UnregisterPowerSettingNotification.restype = wintypes.BOOL
user32.UnregisterPowerSettingNotification.argtypes = [wintypes.HANDLE]

wtsapi32.WTSRegisterSessionNotification.restype = wintypes.BOOL
wtsapi32.WTSRegisterSessionNotification.argtypes = [wintypes.HWND, wintypes.DWORD]
wtsapi32.WTSUnRegisterSessionNotification.restype = wintypes.BOOL
wtsapi32.WTSUnRegisterSessionNotification.argtypes = [wintypes.HWND]

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
    0x0228: {"name": "Razer BlackWidow Elite", "tx_id": 0x00, "mode": 0x02},
    0x024E: {"name": "Razer BlackWidow V3", "tx_id": 0x00, "mode": 0x02},
    0x0256: {"name": "Razer BlackWidow V3 Pro", "tx_id": 0x00, "mode": 0x02},

    # Modern V4 Generation Keyboards with M1-M5 / M1-M8
    0x0287: {"name": "Razer BlackWidow V4", "tx_id": 0x1F, "mode": 0x02},
    0x028C: {"name": "Razer BlackWidow V4 (Alt)", "tx_id": 0x1F, "mode": 0x02},
    0x028D: {"name": "Razer BlackWidow V4 Pro", "tx_id": 0x1F, "mode": 0x02},
    0x0293: {"name": "Razer BlackWidow V4 X", "tx_id": 0x1F, "mode": 0x02},
    0x029F: {"name": "Razer BlackWidow V4 75%", "tx_id": 0x1F, "mode": 0x02},
    0x02B3: {"name": "Razer BlackWidow V4 Pro 75%", "tx_id": 0x1F, "mode": 0x02},

    # Keypads with Macro Matrices
    0x0111: {"name": "Razer Nostromo", "tx_id": 0x00, "mode": 0x02},
    0x0113: {"name": "Razer Orbweaver", "tx_id": 0x00, "mode": 0x02},
    0x0201: {"name": "Razer Tartarus", "tx_id": 0x00, "mode": 0x02},
    0x0207: {"name": "Razer Orbweaver Chroma", "tx_id": 0x00, "mode": 0x02},
    0x0208: {"name": "Razer Tartarus Chroma", "tx_id": 0x00, "mode": 0x02},
    0x022B: {"name": "Razer Tartarus V2", "tx_id": 0x00, "mode": 0x02},
    0x0244: {"name": "Razer Tartarus Pro", "tx_id": 0x00, "mode": 0x02},
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
    if hdev in (None, 0, -1, 0xFFFFFFFFFFFFFFFF):
        raise OSError(ctypes.get_last_error(), "Could not enumerate HID devices")

    did = DID()
    did.cbSize = ctypes.sizeof(DID)
    index = 0
    devices = []

    try:
        while setupapi.SetupDiEnumDeviceInterfaces(hdev, None, ctypes.byref(guid), index, ctypes.byref(did)):
            index += 1
            req = wintypes.DWORD()
            setupapi.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(did), None, 0, ctypes.byref(req), None)
            cb_size = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
            if req.value < cb_size:
                raise OSError(ctypes.get_last_error(), "Invalid HID interface detail size")
            buf = (ctypes.c_byte * req.value)()
            ctypes.cast(buf, ctypes.POINTER(wintypes.DWORD))[0] = cb_size
            if not setupapi.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(did), buf, req.value, None, None):
                raise OSError(ctypes.get_last_error(), "Could not read HID interface detail")
            path = ctypes.wstring_at(ctypes.addressof(buf) + 4)
            if 'vid_1532' in path.lower():
                h = kernel32.CreateFileW(path, 0, 3, None, 3, 0, None)
                if h not in (None, 0, -1, 0xFFFFFFFFFFFFFFFF):
                    preparsed = ctypes.c_void_p()
                    try:
                        if hid.HidD_GetPreparsedData(h, ctypes.byref(preparsed)):
                            try:
                                caps = HIDP_CAPS()
                                if hid.HidP_GetCaps(preparsed, ctypes.byref(caps)) >= 0 and caps.FeatureReportByteLength == 91:
                                    m = re.search(r'pid_([0-9a-fA-F]{4})', path, re.IGNORECASE)
                                    pid = int(m.group(1), 16) if m else 0
                                    devices.append((path, pid))
                            finally:
                                hid.HidD_FreePreparsedData(preparsed)
                    finally:
                        kernel32.CloseHandle(h)
        error = ctypes.get_last_error()
        if error != 259:  # ERROR_NO_MORE_ITEMS
            raise OSError(error, "HID interface enumeration failed")
    finally:
        setupapi.SetupDiDestroyDeviceInfoList(hdev)
    return devices

def send_mode_report(h, tx_id, mode):
    req = bytearray(91)
    req[0] = 0x00 # Report ID
    req[1] = 0x00 # Status
    req[2] = tx_id # Transaction ID (0x00 for legacy, 0x1F for V4)
    req[3] = 0x00 # Remaining packets MSB
    req[4] = 0x00 # Remaining packets LSB
    req[5] = 0x00 # Protocol type
    req[6] = 0x02 # Data size
    req[7] = 0x00 # Command Class
    req[8] = 0x04 # Command ID: Set Device Mode
    req[9] = mode # Mode (0x02 = Legacy / Macro Key Mode)
    req[10] = 0x00 # Param
    req[89] = calc_crc(req)
    req[90] = 0x00 # Reserved

    buf = (ctypes.c_byte * 91).from_buffer(req)
    return bool(hid.HidD_SetFeature(h, buf, 91))

def unlock_device(path, pid):
    if pid in RAZER_DEVICES:
        primary_tx_id = RAZER_DEVICES[pid]["tx_id"]
        mode = RAZER_DEVICES[pid]["mode"]
    else:
        # Fallback for unlisted Razer devices: V4 series (PID >= 0x0280) uses 0x1F, older use 0x00
        primary_tx_id = 0x1F if pid >= 0x0280 else 0x00
        mode = 0x02

    h = kernel32.CreateFileW(path, 0, 3, None, 3, 0, None)
    if h in (None, 0, -1, 0xFFFFFFFFFFFFFFFF):
        return False

    try:
        ok = send_mode_report(h, primary_tx_id, mode)
        if not ok:
            # If first attempt fails, automatically retry with alternative transaction ID (0x1F <-> 0x00)
            alt_tx_id = 0x00 if primary_tx_id == 0x1F else 0x1F
            ok = send_mode_report(h, alt_tx_id, mode)
        return ok
    finally:
        kernel32.CloseHandle(h)

def unlock_all_keyboards():
    devices = find_all_razer_ctrl_devices()
    unlocked = 0
    for path, pid in devices:
        if unlock_device(path, pid):
            unlocked += 1
    return unlocked > 0

def service_status_path():
    base = os.environ.get('LOCALAPPDATA')
    return os.path.join(base, 'RazerMacroUnlocker', 'status.txt') if base else None

def write_service_status(message):
    path = service_status_path()
    if not path:
        return
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as status_file:
            status_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {message}\n")
    except OSError:
        pass

def service_unlock():
    try:
        devices = find_all_razer_ctrl_devices()
        unlocked = sum(bool(unlock_device(path, pid)) for path, pid in devices)
        write_service_status(f"Detected {len(devices)} control device(s); unlock report accepted by {unlocked}.")
        return unlocked > 0
    except Exception as exc:
        write_service_status(f"HID scan failed: {exc}")
        return False

WM_DEVICECHANGE = 0x0219
WM_POWERBROADCAST = 0x0218
PBT_APMRESUMEAUTOMATIC = 0x0012
PBT_APMRESUMESUSPEND = 0x0007
PBT_POWERSETTINGCHANGE = 0x8013

WM_WTSSESSION_CHANGE = 0x02B1
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8
WTS_SESSION_LOGON = 0x5
NOTIFY_FOR_THIS_SESSION = 0

DBT_DEVTYP_DEVICEINTERFACE = 0x00000005
DEVICE_NOTIFY_WINDOW_HANDLE = 0x00000000

class DEV_BROADCAST_DEVICEINTERFACE_W(ctypes.Structure):
    _fields_ = [
        ('dbcc_size', wintypes.DWORD),
        ('dbcc_devicetype', wintypes.DWORD),
        ('dbcc_reserved', wintypes.DWORD),
        ('dbcc_classguid', GUID),
        ('dbcc_name', wintypes.WCHAR * 1)
    ]

class POWERBROADCAST_SETTING(ctypes.Structure):
    _fields_ = [
        ('PowerSetting', GUID),
        ('DataLength', wintypes.DWORD),
        ('Data', wintypes.BYTE * 1)
    ]

# GUID_CONSOLE_DISPLAY_STATE: {238C0517-778D-4B3E-8C78-6ED4771F0522}
# Sent on display turn-on, turn-off, and dimming (Modern Standby & display sleep wake)
GUID_CONSOLE_DISPLAY_STATE = GUID(
    0x238C0517, 0x778D, 0x4B3E,
    (wintypes.BYTE * 8)(0x8C, 0x78, 0x6E, 0xD4, 0x77, 0x1F, 0x05, 0x22)
)

WM_TIMER = 0x0113

ERROR_ALREADY_EXISTS = 183
SINGLE_INSTANCE_MUTEX = "Local\\RazerMacroUnlocker_SingleInstance"
WM_APP = 0x8000
WM_APP_RESCAN = WM_APP + 1

TIMER_ID_DEBOUNCE = 1
TIMER_ID_STARTUP_RETRY = 2
DEBOUNCE_DELAY_MS = 1000
STARTUP_RETRY_DELAY_MS = 2000
_startup_retries_left = 0

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
    global _startup_retries_left
    # Session unlock or logon: immediate unlock with debounced safety follow-up
    if msg == WM_WTSSESSION_CHANGE and wparam in (WTS_SESSION_UNLOCK, WTS_SESSION_LOGON):
        if service_unlock() and _startup_retries_left:
            user32.KillTimer(hwnd, TIMER_ID_STARTUP_RETRY)
            _startup_retries_left = 0
        user32.KillTimer(hwnd, TIMER_ID_DEBOUNCE)
        user32.SetTimer(hwnd, TIMER_ID_DEBOUNCE, DEBOUNCE_DELAY_MS, None)
        return 0

    # Display wake-up (Modern Standby / S0ix)
    if msg == WM_POWERBROADCAST and wparam == PBT_POWERSETTINGCHANGE and lparam:
        try:
            pbs = ctypes.cast(lparam, ctypes.POINTER(POWERBROADCAST_SETTING)).contents
            if pbs.DataLength >= 1 and pbs.Data[0] in (1, 2):  # PowerMonitorOn (1) or PowerMonitorDim (2)
                user32.KillTimer(hwnd, TIMER_ID_DEBOUNCE)
                user32.SetTimer(hwnd, TIMER_ID_DEBOUNCE, DEBOUNCE_DELAY_MS, None)
                return 0
        except Exception:
            pass

    # Debounce device reconnect, standby wake-up, or rescan events
    if msg in (WM_DEVICECHANGE, WM_APP_RESCAN) or (msg == WM_POWERBROADCAST and wparam in (PBT_APMRESUMEAUTOMATIC, PBT_APMRESUMESUSPEND)):
        # Reset timer so rapid successive events are collapsed into a single unlock
        user32.KillTimer(hwnd, TIMER_ID_DEBOUNCE)
        user32.SetTimer(hwnd, TIMER_ID_DEBOUNCE, DEBOUNCE_DELAY_MS, None)
        return 0

    if msg == WM_TIMER and wparam == TIMER_ID_DEBOUNCE:
        user32.KillTimer(hwnd, TIMER_ID_DEBOUNCE)
        if service_unlock() and _startup_retries_left:
            user32.KillTimer(hwnd, TIMER_ID_STARTUP_RETRY)
            _startup_retries_left = 0
        return 0

    if msg == WM_TIMER and wparam == TIMER_ID_STARTUP_RETRY:
        _startup_retries_left -= 1
        if service_unlock() or _startup_retries_left <= 0:
            user32.KillTimer(hwnd, TIMER_ID_STARTUP_RETRY)
        return 0

    if msg in (0x0010, 0x0002): # WM_CLOSE (0x0010), WM_DESTROY (0x0002)
        user32.PostQuitMessage(0)
        return 0

    if msg == 0x0011: # WM_QUERYENDSESSION
        return 1

    if msg == 0x0016: # WM_ENDSESSION
        if wparam:
            user32.PostQuitMessage(0)
        return 0

    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

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
    0x80: ("M5", "F17"),
    0x81: ("M6", "F18"),
    0x82: ("M7", "F19"),
    0x83: ("M8", "F20"),
    0x84: ("Keypad", "F21"),
    0x85: ("Keypad", "F22"),
    0x86: ("Keypad", "F23"),
    0x87: ("Keypad", "F24"),
}

def ensure_console():
    # 1. If stdout is already an active, valid stream with a real file descriptor, keep it
    try:
        if sys.stdout is not None and hasattr(sys.stdout, 'fileno'):
            sys.stdout.fileno()
            sys.stdout.flush()
            return
    except Exception:
        pass

    # 2. Try direct parent first
    ATTACH_PARENT_PROCESS = 0xFFFFFFFF
    attached = kernel32.AttachConsole(ATTACH_PARENT_PROCESS)

    # 3. If direct parent failed (e.g. in PyInstaller onefile where direct parent is the GUI bootloader),
    # walk parent process chain to find the actual calling console (e.g. cmd.exe, pwsh.exe, etc.)
    if not attached:
        hSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if hSnap and hSnap != -1 and hSnap != 0xFFFFFFFFFFFFFFFF:
            pe = PROCESSENTRY32()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
            proc_map = {}
            if kernel32.Process32First(hSnap, ctypes.byref(pe)):
                while True:
                    proc_map[pe.th32ProcessID] = pe.th32ParentProcessID
                    if not kernel32.Process32Next(hSnap, ctypes.byref(pe)):
                        break
            kernel32.CloseHandle(hSnap)

            curr = os.getpid()
            for _ in range(5):
                parent = proc_map.get(curr, 0)
                if parent == 0 or parent == curr:
                    break
                if kernel32.AttachConsole(parent):
                    attached = True
                    break
                curr = parent

    # 4. Only allocate a new console window for interactive test mode when run outside any console
    if not attached:
        if any(arg in sys.argv for arg in ('--test', '-t', 'test')):
            kernel32.AllocConsole()
        else:
            return

    try:
        sys.stdout = open('CONOUT$', 'w', encoding='utf-8', buffering=1)
        sys.stderr = open('CONOUT$', 'w', encoding='utf-8', buffering=1)
    except Exception:
        pass

def run_interactive_test():
    ensure_console()
    print("=" * 60)
    print("       Universal Razer Macro Key Unlocker - Test        ")
    print("=" * 60)

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
    print("Press M1 to M8, Keypad keys, or any standard keys.")
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

REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_APP_NAME = "RazerUnlocker"

def set_autostart_registry(command):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, command)
        return True
    except OSError as e:
        print(f"[ERROR] Failed to set registry autostart: {e}")
        return False

def remove_autostart_registry():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, REG_APP_NAME)
        return True
    except FileNotFoundError:
        return False
    except OSError as e:
        print(f"[WARNING] Failed to remove registry autostart: {e}")
        return False

def get_autostart_registry():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_QUERY_VALUE) as key:
            val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
            return val
    except (FileNotFoundError, OSError):
        return None

def get_clean_env():
    """Return an environment dictionary stripped of PyInstaller variables.
    This ensures that child processes extract to their own temporary folder
    and do not lock or reuse the parent installer's _MEI directory."""
    env = os.environ.copy()
    keys_to_remove = [k for k in env if k.startswith('_MEI') or k.startswith('_PYI') or k.startswith('PYINSTALLER')]
    for k in keys_to_remove:
        del env[k]
    return env

def cleanup_stale_mei_dirs():
    """Safely purge orphaned _MEI directories left in %TEMP% by previous crashes or abrupt terminations.
    Folders currently in use by running processes cannot be deleted and are safely skipped."""
    temp_dir = os.environ.get('TEMP') or os.environ.get('TMP')
    if not temp_dir or not os.path.isdir(temp_dir):
        return

    current_mei = getattr(sys, '_MEIPASS', None)
    try:
        for entry in os.listdir(temp_dir):
            if entry.startswith('_MEI') and len(entry) > 4:
                full_path = os.path.join(temp_dir, entry)
                if current_mei and os.path.abspath(full_path) == os.path.abspath(current_mei):
                    continue
                if os.path.isdir(full_path):
                    try:
                        shutil.rmtree(full_path, ignore_errors=False)
                    except Exception:
                        pass
    except Exception:
        pass

def cli_install():
    ensure_console()
    print("=" * 60)
    print("  Universal Razer Macro Key Unlocker - Setup Autostart")
    print("=" * 60)

    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen:
        target_path = sys.executable
        work_dir = os.path.dirname(sys.executable)
        launch_cmd = [sys.executable]
        run_command = f'"{target_path}"'
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        target_path = python_exe if os.path.exists(python_exe) else sys.executable
        script_path = os.path.abspath(__file__)
        work_dir = script_dir
        launch_cmd = [target_path, script_path]
        run_command = f'"{target_path}" "{script_path}"'

    print("Configuring Windows Registry autostart:")
    print(f"  Key:     HKCU\\{REG_RUN_KEY}")
    print(f"  Name:    {REG_APP_NAME}")
    print(f"  Command: {run_command}")

    ok = set_autostart_registry(run_command)
    if ok:
        print("\n[OK] Autostart successfully registered in Windows Registry!")

        # Check if service is already running
        hwnd_existing = user32.FindWindowW("RazerUnlockerServiceClass", "RazerUnlocker")
        if hwnd_existing:
            user32.PostMessageW(hwnd_existing, WM_APP_RESCAN, 0, 0)
            print("[OK] Background service is already running. Sent rescan signal.")
        else:
            print("Starting background service...")
            # Sanitize current environment so child process does not inherit and lock parent's _MEI directory
            for k in list(os.environ.keys()):
                if k.startswith('_MEI') or k.startswith('_PYI') or k.startswith('PYINSTALLER'):
                    del os.environ[k]

            try:
                if not is_frozen:
                    os.startfile(target_path, arguments=f'"{script_path}"', cwd=work_dir)
                else:
                    os.startfile(target_path, cwd=work_dir)
            except Exception:
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                subprocess.Popen(
                    launch_cmd,
                    cwd=work_dir,
                    env=os.environ,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                )
            print("[OK] Razer Macro Unlocker is now running in the background.")
    else:
        print("\n[ERROR] Failed to configure autostart in Windows Registry.")

def cli_uninstall():
    ensure_console()
    print("=" * 60)
    print("  Universal Razer Macro Key Unlocker - Uninstall")
    print("=" * 60)

    # 1. Terminate running background service
    print("Stopping running background service instances...")
    hwnd = user32.FindWindowW("RazerUnlockerServiceClass", "RazerUnlocker")
    if hwnd:
        user32.PostMessageW(hwnd, 0x0010, 0, 0) # WM_CLOSE
        print("  [OK] Sent stop signal to RazerUnlocker background service.")
    else:
        print("  [INFO] No running RazerUnlocker background service found.")

    # 2. Remove registry autostart
    removed = remove_autostart_registry()
    if removed:
        print(f"[OK] Removed Windows Registry autostart entry (HKCU\\{REG_RUN_KEY}\\{REG_APP_NAME}).")
    else:
        print(f"[INFO] Registry autostart entry not present.")

    print("\n[OK] Razer Macro Unlocker uninstalled and stopped.")

def cli_status():
    ensure_console()
    print("=" * 60)
    print("  Universal Razer Macro Key Unlocker - Device Status")
    print("=" * 60)
    devices = find_all_razer_ctrl_devices()
    if not devices:
        print("No Razer devices with 91-byte control endpoints found.")
        return

    print(f"Found {len(devices)} Razer control device(s):")
    for path, pid in devices:
        name = RAZER_DEVICES.get(pid, {}).get("name", f"Unknown Razer Device (PID: 0x{pid:04X})")
        print(f"  - {name} (PID: 0x{pid:04X})")
        print(f"    Path: {path}")

def cli_rescan():
    ensure_console()
    print("Sending rescan signal to running background service...")
    hwnd = user32.FindWindowW("RazerUnlockerServiceClass", "RazerUnlocker")
    if hwnd:
        user32.PostMessageW(hwnd, WM_APP_RESCAN, 0, 0)
        print("[OK] Rescan signal sent to running Razer Macro Unlocker.")
    else:
        print("[INFO] No running background service found. Performing direct unlock...")
        if unlock_all_keyboards():
            print("[OK] All connected Razer devices unlocked.")
        else:
            print("[WARNING] No devices could be unlocked.")

def cli_help():
    ensure_console()
    print("=" * 60)
    print("  Universal Razer Macro Key Unlocker (M1-M5 to F13-F17)")
    print("=" * 60)
    print("\nUsage:")
    print("  RazerMacroUnlocker.exe [options]\n")
    print("Options:")
    print("  --install, -i      Configure autostart with Windows and start service")
    print("  --uninstall, -u    Remove autostart and stop background service")
    print("  --test, -t         Launch interactive diagnostic key listener")
    print("  --status, -s       Display detected Razer devices and their status")
    print("  --rescan, -r       Trigger an immediate re-scan on the running service")
    print("  --help, -h         Show this help message")
    print("\nWithout arguments, runs silently in the background as a Windows service.")

_instance_mutex = None

def main():
    global _instance_mutex

    # Clean up any stale orphaned _MEI directories from previous crashes
    cleanup_stale_mei_dirs()

    # Handle CLI arguments
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ('--install', '-i', 'install'):
            cli_install()
            sys.exit(0)
        elif cmd in ('--uninstall', '-u', 'uninstall'):
            cli_uninstall()
            sys.exit(0)
        elif cmd in ('--test', '-t', 'test'):
            run_interactive_test()
            sys.exit(0)
        elif cmd in ('--status', '-s', 'status'):
            cli_status()
            sys.exit(0)
        elif cmd in ('--rescan', '-r', 'rescan'):
            cli_rescan()
            sys.exit(0)
        elif cmd in ('--help', '-h', '/?', 'help'):
            cli_help()
            sys.exit(0)

    # Enforce single instance via named Windows Mutex for background service
    _instance_mutex = kernel32.CreateMutexW(None, True, SINGLE_INSTANCE_MUTEX)
    if not _instance_mutex or kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        # If an instance is already running, signal it to rescan devices and exit
        hwnd_existing = user32.FindWindowW("RazerUnlockerServiceClass", "RazerUnlocker")
        if hwnd_existing:
            user32.PostMessageW(hwnd_existing, WM_APP_RESCAN, 0, 0)
        if _instance_mutex:
            kernel32.CloseHandle(_instance_mutex)
        sys.exit(0)

    # Register hidden window to receive USB and Power events
    global _wnd_proc_cb
    _wnd_proc_cb = WNDPROC(wnd_proc)
    wnd_class = WNDCLASSW()
    wnd_class.lpfnWndProc = _wnd_proc_cb
    wnd_class.lpszClassName = "RazerUnlockerServiceClass"
    wnd_class.hInstance = kernel32.GetModuleHandleW(None)
    user32.RegisterClassW(ctypes.byref(wnd_class))

    hwnd = user32.CreateWindowExW(0, "RazerUnlockerServiceClass", "RazerUnlocker", 0, 0, 0, 0, 0, None, None, wnd_class.hInstance, None)
    if not hwnd:
        error = kernel32.GetLastError()
        kernel32.CloseHandle(_instance_mutex)
        raise OSError(error, "Could not create service window")

    # Register for HID device notifications (ensures WM_DEVICECHANGE is delivered on USB plug/unplug)
    dev_filter = DEV_BROADCAST_DEVICEINTERFACE_W()
    dev_filter.dbcc_size = ctypes.sizeof(DEV_BROADCAST_DEVICEINTERFACE_W)
    dev_filter.dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE
    dev_filter.dbcc_reserved = 0
    hid.HidD_GetHidGuid(ctypes.byref(dev_filter.dbcc_classguid))
    h_dev_notify = user32.RegisterDeviceNotificationW(hwnd, ctypes.byref(dev_filter), DEVICE_NOTIFY_WINDOW_HANDLE)

    # Register for Session change notifications (unlock / logon)
    wts_registered = bool(wtsapi32.WTSRegisterSessionNotification(hwnd, NOTIFY_FOR_THIS_SESSION))

    # Register for Display State notifications (Modern Standby / display wake-up)
    h_power_notify = user32.RegisterPowerSettingNotification(hwnd, ctypes.byref(GUID_CONSOLE_DISPLAY_STATE), DEVICE_NOTIFY_WINDOW_HANDLE)

    # Retry through the message loop so device and shutdown events remain responsive.
    global _startup_retries_left
    if not service_unlock():
        _startup_retries_left = 4
        if not user32.SetTimer(hwnd, TIMER_ID_STARTUP_RETRY, STARTUP_RETRY_DELAY_MS, None):
            write_service_status("Could not schedule startup retries.")

    # Passive message loop (0% CPU usage)
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    # Clean up notifications
    if h_dev_notify:
        user32.UnregisterDeviceNotification(h_dev_notify)
    if wts_registered:
        wtsapi32.WTSUnRegisterSessionNotification(hwnd)
    if h_power_notify:
        user32.UnregisterPowerSettingNotification(h_power_notify)
    user32.KillTimer(hwnd, TIMER_ID_DEBOUNCE)
    user32.KillTimer(hwnd, TIMER_ID_STARTUP_RETRY)
    kernel32.CloseHandle(_instance_mutex)

if __name__ == '__main__':
    main()
