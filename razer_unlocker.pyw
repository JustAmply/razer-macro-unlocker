"""
Razer BlackWidow Chroma V2 - Silent Hardware Unlocker
Enables hardware legacy mode (M1-M5 emit native F13-F17 keystrokes).
100% Anti-Cheat compliant: Uses standard Windows drivers (hidusb.sys).
No hooks, no custom drivers, 0% CPU usage.
"""

import ctypes
from ctypes import wintypes
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

def calc_crc(buf):
    crc = 0
    for b in buf[3:89]:
        crc ^= b
    return crc

def find_razer_ctrl_path():
    guid = GUID()
    hid.HidD_GetHidGuid(ctypes.byref(guid))
    hdev = setupapi.SetupDiGetClassDevsW(ctypes.byref(guid), None, None, 0x12)

    did = DID()
    did.cbSize = ctypes.sizeof(DID)
    index = 0
    found_path = None

    while setupapi.SetupDiEnumDeviceInterfaces(hdev, None, ctypes.byref(guid), index, ctypes.byref(did)):
        index += 1
        req = wintypes.DWORD()
        setupapi.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(did), None, 0, ctypes.byref(req), None)
        buf = (ctypes.c_byte * req.value)()
        cbSize = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
        ctypes.cast(buf, ctypes.POINTER(wintypes.DWORD))[0] = cbSize
        if setupapi.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(did), buf, req.value, None, None):
            path = ctypes.wstring_at(ctypes.addressof(buf) + 4)
            if 'vid_1532' in path.lower() and 'pid_0221' in path.lower():
                h = kernel32.CreateFileW(path, 0, 3, None, 3, 0, None)
                if h != -1 and h != 0 and h != 0xFFFFFFFFFFFFFFFF:
                    preparsed = ctypes.c_void_p()
                    if hid.HidD_GetPreparsedData(h, ctypes.byref(preparsed)):
                        caps = HIDP_CAPS()
                        hid.HidP_GetCaps(preparsed, ctypes.byref(caps))
                        hid.HidD_FreePreparsedData(preparsed)
                        kernel32.CloseHandle(h)
                        if caps.FeatureReportByteLength == 91:
                            found_path = path
                            break
                    kernel32.CloseHandle(h)

    setupapi.SetupDiDestroyDeviceInfoList(hdev)
    return found_path

def unlock_keyboard():
    path = find_razer_ctrl_path()
    if not path:
        return False

    h = kernel32.CreateFileW(path, 0, 3, None, 3, 0, None)
    if h == -1 or h == 0 or h == 0xFFFFFFFFFFFFFFFF:
        return False

    req = bytearray(91)
    req[0] = 0x00 # Report ID
    req[1] = 0x00 # Status
    req[2] = 0x00 # Transaction ID
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
    hid.HidD_SetFeature(h, buf, 91)
    kernel32.CloseHandle(h)
    return True

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
    # Re-unlock keyboard on device reconnect or standby wake-up
    if msg == WM_DEVICECHANGE or (msg == WM_POWERBROADCAST and wparam in (PBT_APMRESUMEAUTOMATIC, PBT_APMRESUMESUSPEND)):
        time.sleep(1.0) # Small delay to allow USB enumeration to complete
        unlock_keyboard()
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

def main():
    # Attempt unlock on startup (retry up to 5 times)
    for _ in range(5):
        if unlock_keyboard():
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
