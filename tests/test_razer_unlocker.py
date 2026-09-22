"""Isolated contract tests for the Windows HID and command-line seams."""

import ctypes
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "razer_unlocker.pyw"
SPEC = importlib.util.spec_from_file_location("razer_unlocker", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load application module from {MODULE_PATH}")
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class HidEnumerationTests(unittest.TestCase):
    def test_invalid_device_information_handles_are_rejected(self):
        for handle in (None, 0, -1, 0xFFFFFFFFFFFFFFFF):
            with self.subTest(handle=handle):
                with mock.patch.object(
                    app.setupapi, "SetupDiGetClassDevsW", return_value=handle
                ), mock.patch.object(app.hid, "HidD_GetHidGuid"):
                    with self.assertRaisesRegex(OSError, "Could not enumerate HID"):
                        app.find_all_razer_ctrl_devices()

    def test_too_small_interface_detail_size_raises_and_releases_device_list(self):
        device_info_set = 0x1234

        def enumerate_interfaces(_set, _device, _guid, index, _interface):
            if index == 0:
                return True
            return False

        def get_interface_detail(
            _set, _interface, detail, _detail_size, required_size, _device_info
        ):
            if detail is None:
                ctypes.cast(
                    required_size, ctypes.POINTER(app.wintypes.DWORD)
                ).contents.value = 4
            return False

        with (
            mock.patch.object(app.hid, "HidD_GetHidGuid"),
            mock.patch.object(
                app.setupapi,
                "SetupDiGetClassDevsW",
                return_value=device_info_set,
            ),
            mock.patch.object(
                app.setupapi,
                "SetupDiEnumDeviceInterfaces",
                side_effect=enumerate_interfaces,
            ),
            mock.patch.object(
                app.setupapi,
                "SetupDiGetDeviceInterfaceDetailW",
                side_effect=get_interface_detail,
            ),
            mock.patch.object(
                app.setupapi, "SetupDiDestroyDeviceInfoList", return_value=True
            ) as destroy_device_list,
        ):
            with self.assertRaisesRegex(OSError, "Invalid HID interface detail size"):
                app.find_all_razer_ctrl_devices()

        destroy_device_list.assert_called_once_with(device_info_set)

    def test_enumeration_returns_razer_path_and_releases_native_handles(self):
        device_info_set = 0x1234
        device_handle = 0x5678
        preparsed_data = 0x9ABC
        path = r"\\?\hid#vid_1532&pid_0287&mi_00#device#{guid}"
        encoded_path = path.encode("utf-16-le") + b"\0\0"
        required_length = max(8, 4 + len(encoded_path))
        closed_handles = []

        def enumerate_interfaces(_set, _device, _guid, index, _interface):
            if index == 0:
                return True
            return False

        def get_interface_detail(
            _set, _interface, detail, _detail_size, required_size, _device_info
        ):
            if detail is None:
                ctypes.cast(
                    required_size, ctypes.POINTER(app.wintypes.DWORD)
                ).contents.value = required_length
                return False
            ctypes.memmove(ctypes.addressof(detail) + 4, encoded_path, len(encoded_path))
            return True

        def get_preparsed_data(_handle, data_pointer):
            ctypes.cast(data_pointer, ctypes.POINTER(ctypes.c_void_p)).contents.value = (
                preparsed_data
            )
            return True

        def get_caps(_data, caps_pointer):
            ctypes.cast(
                caps_pointer, ctypes.POINTER(app.HIDP_CAPS)
            ).contents.FeatureReportByteLength = 91
            return 0

        with (
            mock.patch.object(app.hid, "HidD_GetHidGuid"),
            mock.patch.object(
                app.setupapi,
                "SetupDiGetClassDevsW",
                return_value=device_info_set,
            ),
            mock.patch.object(
                app.setupapi,
                "SetupDiEnumDeviceInterfaces",
                side_effect=enumerate_interfaces,
            ),
            mock.patch.object(ctypes, "get_last_error", return_value=259),
            mock.patch.object(
                app.setupapi,
                "SetupDiGetDeviceInterfaceDetailW",
                side_effect=get_interface_detail,
            ),
            mock.patch.object(
                app.setupapi, "SetupDiDestroyDeviceInfoList", return_value=True
            ) as destroy_device_list,
            mock.patch.object(
                app.kernel32, "CreateFileW", return_value=device_handle
            ),
            mock.patch.object(app.kernel32, "CloseHandle", side_effect=closed_handles.append),
            mock.patch.object(
                app.hid, "HidD_GetPreparsedData", side_effect=get_preparsed_data
            ),
            mock.patch.object(app.hid, "HidD_FreePreparsedData", return_value=True) as free_data,
            mock.patch.object(app.hid, "HidP_GetCaps", side_effect=get_caps),
        ):
            devices = app.find_all_razer_ctrl_devices()

        self.assertEqual(devices, [(path, 0x0287)])
        self.assertEqual(closed_handles, [device_handle])
        free_data.assert_called_once()
        destroy_device_list.assert_called_once_with(device_info_set)

    def test_unlock_rejects_invalid_file_handles_without_sending_a_report(self):
        for handle in (None, 0, -1, 0xFFFFFFFFFFFFFFFF):
            with self.subTest(handle=handle):
                with (
                    mock.patch.object(
                        app.kernel32, "CreateFileW", return_value=handle
                    ),
                    mock.patch.object(app.kernel32, "CloseHandle") as close_handle,
                    mock.patch.object(app, "send_mode_report") as send_report,
                ):
                    self.assertFalse(app.unlock_device("device-path", 0x0287))

                close_handle.assert_not_called()
                send_report.assert_not_called()


class FeatureReportTests(unittest.TestCase):
    def test_crc_matches_known_xor_vector(self):
        self.assertEqual(app.calc_crc(bytes(range(91))), 0x5B)

    def test_mode_report_matches_golden_bytes_and_crc(self):
        sent = {}

        def capture_report(handle, report, length):
            sent["handle"] = handle
            sent["length"] = length
            sent["bytes"] = ctypes.string_at(ctypes.addressof(report), length)
            return True

        with mock.patch.object(app.hid, "HidD_SetFeature", side_effect=capture_report):
            result = app.send_mode_report(0x1234, 0x1F, 0x02)

        expected = bytes([0x00, 0x00, 0x1F, 0x00, 0x00, 0x00, 0x02, 0x00, 0x04, 0x02])
        expected += bytes(79) + bytes([0x04, 0x00])
        self.assertTrue(result)
        self.assertEqual(sent, {"handle": 0x1234, "length": 91, "bytes": expected})


class CommandLineTests(unittest.TestCase):
    def assert_command_exit_code(self, option, handler_name, return_code):
        handler = mock.Mock(return_value=return_code)
        with (
            mock.patch.object(app.sys, "argv", [str(MODULE_PATH), option]),
            mock.patch.object(app, handler_name, handler),
        ):
            with self.assertRaises(SystemExit) as raised:
                app.main()

        handler.assert_called_once_with()
        self.assertEqual(raised.exception.code, return_code)

    def test_status_command_propagates_success_and_failure_exit_codes(self):
        for return_code in (0, 4):
            with self.subTest(return_code=return_code):
                self.assert_command_exit_code("--status", "cli_status", return_code)

    def test_rescan_command_propagates_success_and_failure_exit_codes(self):
        for return_code in (0, 5):
            with self.subTest(return_code=return_code):
                self.assert_command_exit_code("--rescan", "cli_rescan", return_code)

    def test_unknown_option_exits_with_nonzero_status_without_starting_service(self):
        with (
            mock.patch.object(app.sys, "argv", [str(MODULE_PATH), "--unknown-option"]),
            mock.patch.object(app, "ensure_console"),
            mock.patch.object(app.kernel32, "CreateMutexW") as create_mutex,
        ):
            with self.assertRaises(SystemExit) as raised:
                app.main()

        self.assertNotEqual(raised.exception.code, 0)
        create_mutex.assert_not_called()

    def test_rescan_reports_post_failure(self):
        with (
            mock.patch.object(app, "ensure_console"),
            mock.patch.object(app.user32, "FindWindowW", return_value=123),
            mock.patch.object(app.user32, "PostMessageW", return_value=0),
        ):
            self.assertEqual(app.cli_rescan(), 1)

    def test_uninstall_reports_registry_failure(self):
        with (
            mock.patch.object(app, "ensure_console"),
            mock.patch.object(app.user32, "FindWindowW", return_value=0),
            mock.patch.object(app, "remove_autostart_registry", return_value=False),
        ):
            self.assertEqual(app.cli_uninstall(), 1)

    def test_install_reports_registry_failure_without_starting_service(self):
        with (
            mock.patch.object(app, "ensure_console"),
            mock.patch.object(app, "set_autostart_registry", return_value=False),
            mock.patch.object(app.user32, "FindWindowW") as find_window,
        ):
            self.assertEqual(app.cli_install(), 1)
        find_window.assert_not_called()

    def test_install_allows_delayed_one_file_startup(self):
        with (
            mock.patch.object(app, "ensure_console"),
            mock.patch.object(app, "set_autostart_registry", return_value=True),
            mock.patch.object(app.user32, "FindWindowW", side_effect=[0] * 31 + [123]),
            mock.patch.object(app.subprocess, "Popen"),
            mock.patch.object(app.time, "sleep") as sleep,
        ):
            self.assertEqual(app.cli_install(), 0)
        self.assertEqual(sleep.call_count, 30)

    def test_status_distinguishes_detection_from_unlock(self):
        with (
            mock.patch.object(app, "ensure_console"),
            mock.patch.object(app.user32, "FindWindowW", return_value=123),
            mock.patch.object(app, "get_autostart_registry", return_value="command"),
            mock.patch.object(app, "find_all_razer_ctrl_devices", return_value=[("hid-path", 0x0287)]),
            mock.patch.object(app, "service_status_path", return_value=None),
            mock.patch("builtins.print") as output,
        ):
            self.assertEqual(app.cli_status(), 0)
        lines = [str(call.args[0]) for call in output.call_args_list if call.args]
        self.assertIn("Background service: running", lines)
        self.assertIn("Autostart: configured", lines)
        self.assertTrue(any("cannot be inferred" in line for line in lines))


class ServiceTests(unittest.TestCase):
    def test_startup_retry_timer_stops_after_success(self):
        app._startup_retries_left = 4
        with (
            mock.patch.object(app, "service_unlock", return_value=True) as unlock,
            mock.patch.object(app.user32, "KillTimer") as kill_timer,
        ):
            self.assertEqual(app.wnd_proc(123, app.WM_TIMER, app.TIMER_ID_STARTUP_RETRY, 0), 0)
        unlock.assert_called_once()
        kill_timer.assert_called_once_with(123, app.TIMER_ID_STARTUP_RETRY)
        self.assertEqual(app._startup_retries_left, 3)

    def test_service_unlock_records_scan_error(self):
        with (
            mock.patch.object(app, "find_all_razer_ctrl_devices", side_effect=OSError("scan failed")),
            mock.patch.object(app, "write_service_status") as write_status,
        ):
            self.assertFalse(app.service_unlock())
        self.assertIn("scan failed", write_status.call_args.args[0])

    def test_startup_retry_stops_after_final_attempt(self):
        app._startup_retries_left = 1
        with (
            mock.patch.object(app, "service_unlock", return_value=False),
            mock.patch.object(app.user32, "KillTimer") as kill_timer,
        ):
            self.assertEqual(app.wnd_proc(123, app.WM_TIMER, app.TIMER_ID_STARTUP_RETRY, 0), 0)
        self.assertEqual(app._startup_retries_left, 0)
        kill_timer.assert_called_once_with(123, app.TIMER_ID_STARTUP_RETRY)


if __name__ == "__main__":
    unittest.main()
