"""Connected controller discovery with synthetic BlueZ command responses."""

import subprocess
import unittest
from unittest.mock import call, patch

from tests.helper_loader import load_helper


def completed(stdout="", returncode=0):
    return subprocess.CompletedProcess([], returncode, stdout, "")


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper("gaming")
        self.which = patch.object(self.helper.shutil, "which", return_value="/usr/bin/bluetoothctl")
        self.which_mock = self.which.start()
        self.addCleanup(self.which.stop)

    def test_missing_bluetoothctl_returns_empty_without_commands(self):
        self.which_mock.return_value = None
        with patch.object(self.helper.subprocess, "run") as run:
            self.assertEqual(self.helper.controllers(), [])
        run.assert_not_called()
        self.which_mock.assert_called_once_with("bluetoothctl")

    def test_failed_connected_device_query_returns_empty_without_info_queries(self):
        with patch.object(self.helper.subprocess, "run", return_value=completed(returncode=1)) as run:
            self.assertEqual(self.helper.controllers(), [])
        run.assert_called_once_with(["bluetoothctl", "devices", "Connected"], capture_output=True, text=True, timeout=8)

    def test_filters_malformed_lines_and_non_controller_devices(self):
        devices = "\n".join([
            "[NEW] Device AA:BB:CC:DD:EE:00 Xbox Controller",
            "Device invalid Xbox Controller",
            "Device AA:BB:CC:DD:EE:01 Headphones",
            "Device AA:BB:CC:DD:EE:02 Xbox Wireless Controller",
        ])
        with patch.object(self.helper.subprocess, "run", side_effect=[completed(devices), completed("Icon: audio-card"), completed("Battery Percentage: 75")]) as run:
            result = self.helper.controllers()
        self.assertEqual(result, [{"name": "Xbox Wireless Controller", "mac": "AA:BB:CC:DD:EE:02", "battery": 75}])
        self.assertEqual(run.call_args_list, [
            call(["bluetoothctl", "devices", "Connected"], capture_output=True, text=True, timeout=8),
            call(["bluetoothctl", "info", "AA:BB:CC:DD:EE:01"], capture_output=True, text=True, timeout=8),
            call(["bluetoothctl", "info", "AA:BB:CC:DD:EE:02"], capture_output=True, text=True, timeout=8),
        ])

    def test_common_controller_names_are_recognized_case_insensitively(self):
        for name in ("Xbox Wireless Controller", "DualShock 4", "DualSense Wireless", "8BitDo Ultimate", "Nintendo Pro Controller", "Generic GAMEPAD", "Joypad"):
            with self.subTest(name=name):
                with patch.object(self.helper.subprocess, "run", side_effect=[completed("Device aa:bb:cc:dd:ee:ff " + name), completed("")]):
                    result = self.helper.controllers()
                self.assertEqual(result, [{"name": name, "mac": "aa:bb:cc:dd:ee:ff", "battery": None}])

    def test_battery_parses_decimal_and_bluez_hex_with_decimal_annotation(self):
        for detail, expected in (("Battery Percentage: 0x64 (100)", 100), ("Battery Percentage: 0x00 (0)", 0), ("Battery Percentage: 0x4b (75)", 75), ("Battery Percentage: 42", 42), ("Battery Percentage: 100", 100)):
            with self.subTest(detail=detail):
                with patch.object(self.helper.subprocess, "run", side_effect=[completed("Device AA:BB:CC:DD:EE:FF Gamepad"), completed(detail)]):
                    self.assertEqual(self.helper.controllers()[0]["battery"], expected)

    def test_missing_invalid_and_out_of_range_battery_remain_unknown(self):
        for detail in ("", "Battery Percentage: unavailable", "Battery Percentage: -1", "Battery Percentage: 101", "Battery Percentage: 255"):
            with self.subTest(detail=detail):
                with patch.object(self.helper.subprocess, "run", side_effect=[completed("Device AA:BB:CC:DD:EE:FF Gamepad"), completed(detail)]):
                    self.assertIsNone(self.helper.controllers()[0]["battery"])

    def test_at_most_four_controllers_are_queried_and_returned(self):
        devices = "\n".join("Device AA:BB:CC:DD:EE:0" + str(i) + " Gamepad " + str(i) for i in range(6))
        with patch.object(self.helper.subprocess, "run", side_effect=[completed(devices)] + [completed("")] * 4) as run:
            result = self.helper.controllers()
        self.assertEqual([item["name"] for item in result], ["Gamepad 0", "Gamepad 1", "Gamepad 2", "Gamepad 3"])
        self.assertEqual(run.call_count, 5)

    def test_os_errors_and_timeouts_return_empty(self):
        for error in (OSError("bluetooth unavailable"), subprocess.TimeoutExpired("bluetoothctl", 8)):
            with self.subTest(error=type(error).__name__):
                with patch.object(self.helper.subprocess, "run", side_effect=error):
                    self.assertEqual(self.helper.controllers(), [])

    def test_detail_timeout_is_caught(self):
        with patch.object(self.helper.subprocess, "run", side_effect=[completed("Device AA:BB:CC:DD:EE:FF Gamepad"), subprocess.TimeoutExpired("bluetoothctl", 8)]):
            self.assertEqual(self.helper.controllers(), [])

    @unittest.expectedFailure
    def test_known_issue_generic_hid_keyboard_is_not_a_game_controller(self):
        # Baseline treats every Human Interface Device UUID as a controller signal.
        with patch.object(self.helper.subprocess, "run", side_effect=[
            completed("Device AA:BB:CC:DD:EE:FF Office Keyboard"),
            completed("Icon: input-keyboard\nUUID: Human Interface Device (00001124-0000-1000-8000-00805f9b34fb)\nBattery Percentage: 99"),
        ]):
            self.assertEqual(self.helper.controllers(), [])


if __name__ == "__main__":
    unittest.main()
