"""Profile parsing and action guards against mocked command output."""

import contextlib
import io
import json
import runpy
import subprocess
import sys
import unittest
from unittest.mock import call, patch

from tests.helper_loader import HELPERS, load_helper

PROFILE_OUTPUT = """Available profiles:
  quiet          Quiet firmware preset
* balanced       Balanced firmware preset
  performance    Performance firmware preset
  turbo-game     Custom 65 W profile
  eco-2          Battery profile
  turbo-game     Updated description
  custom         Current manual state
  invalid_single_space description
  BadUpper       Ignored heading
"""


def completed(stdout="", stderr="", returncode=0):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


class SafeLoaderTests(unittest.TestCase):
    def test_loading_helpers_does_not_dispatch_commands_or_print(self):
        output = io.StringIO()
        with patch("subprocess.run") as run, patch("subprocess.Popen") as popen:
            with contextlib.redirect_stdout(output):
                control = load_helper("control")
                gaming = load_helper("gaming")
        run.assert_not_called()
        popen.assert_not_called()
        self.assertEqual(output.getvalue(), "")
        self.assertTrue(callable(control.main))
        self.assertTrue(callable(gaming.launch))


class HelperEntryPointTests(unittest.TestCase):
    def execute(self, helper, args):
        output = io.StringIO()
        with patch.object(sys, "argv", [str(HELPERS[helper]), *args]):
            with contextlib.redirect_stdout(output):
                runpy.run_path(str(HELPERS[helper]), run_name="__main__")
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 1, "The helper must emit exactly one JSON object")
        return json.loads(lines[0])

    def test_control_invalid_cli_action_returns_json_without_commands(self):
        with patch("subprocess.run") as run, patch("subprocess.Popen") as popen:
            result = self.execute("control", ["unknown"])
        self.assertEqual(result, {"ok": False, "error": "Unsupported command"})
        run.assert_not_called()
        popen.assert_not_called()

    def test_gaming_invalid_cli_action_and_arity_return_json_without_commands(self):
        for args in (["unknown"], ["launch"], ["launch", "quiet", "extra"]):
            with self.subTest(args=args):
                with patch("subprocess.run") as run, patch("subprocess.Popen") as popen:
                    result = self.execute("gaming", args)
                self.assertEqual(result, {"ok": False, "error": "Invalid command"})
                run.assert_not_called()
                popen.assert_not_called()

    def test_missing_z13ctl_is_serialized_as_an_error(self):
        for helper, args in (("control", []), ("gaming", ["launch", "quiet"])):
            with self.subTest(helper=helper):
                with patch("subprocess.run", side_effect=FileNotFoundError("z13ctl missing")), patch("subprocess.Popen") as popen:
                    result = self.execute(helper, args)
                self.assertEqual(result, {"ok": False, "error": "z13ctl missing"})
                popen.assert_not_called()

    def test_missing_session_selector_is_serialized_before_profile_change(self):
        with patch("subprocess.run", return_value=completed(PROFILE_OUTPUT)) as run, patch("subprocess.Popen") as popen, patch("shutil.which", return_value=None):
            result = self.execute("gaming", ["launch", "quiet"])
        self.assertEqual(result, {"ok": False, "error": "steamos-session-select missing; no session change made"})
        run.assert_called_once_with(["z13ctl", "profile", "--list"], capture_output=True, text=True, timeout=12)
        popen.assert_not_called()


class ControlProfileTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper("control")

    def test_profiles_preserve_firmware_order_and_deduplicate(self):
        with patch.object(self.helper, "run", return_value=PROFILE_OUTPUT) as run:
            self.assertEqual(self.helper.profiles(), [
                "quiet", "balanced", "performance", "turbo-game", "eco-2", "custom"
            ])
        run.assert_called_once_with("profile", "--list")

    def test_empty_list_keeps_firmware_defaults(self):
        with patch.object(self.helper, "run", return_value=""):
            self.assertEqual(self.helper.profiles(), ["quiet", "balanced", "performance"])

    def test_details_use_last_description_for_duplicate_name(self):
        with patch.object(self.helper, "run", return_value=PROFILE_OUTPUT):
            details = self.helper.profile_details()
        self.assertEqual(details["turbo-game"], "Updated description")
        self.assertEqual(details["balanced"], "Balanced firmware preset")
        self.assertNotIn("invalid_single_space", details)
        self.assertNotIn("BadUpper", details)

    def test_status_parses_real_labels(self):
        outputs = {
            ("status",): "Profile: turbo-game (custom)\nAPU: 62 C\nFans: 2200 RPM\nPower: 42 W\nTDP: 45W / 65W\nUV: -10 mV\n",
            ("autoswitch", "--get"): "Autoswitch: enabled\n  AC: turbo-game\n  Battery: eco-2\n",
            ("profile", "--list"): PROFILE_OUTPUT,
        }
        with patch.object(self.helper, "run", side_effect=lambda *args: outputs[args]):
            result = self.helper.status()
        self.assertTrue(result["ok"])
        self.assertTrue(result["autoswitch"])
        self.assertEqual(result["active"], "turbo-game")
        self.assertEqual(result["ac"], "turbo-game")
        self.assertEqual(result["battery"], "eco-2")
        self.assertEqual(result["temp"], "62 C")
        self.assertEqual(result["fan"], "2200 RPM")
        self.assertEqual(result["power"], "42 W")
        self.assertEqual(result["tdp"], "45W / 65W")
        self.assertEqual(result["uv"], "-10 mV")
        self.assertEqual(result["details"]["eco-2"], "Battery profile")

    def test_status_missing_fields_are_empty_and_autoswitch_disabled(self):
        with patch.object(self.helper, "run", return_value=""):
            result = self.helper.status()
        self.assertFalse(result["autoswitch"])
        for key in ("active", "ac", "battery", "temp", "fan", "power", "tdp", "uv"):
            with self.subTest(field=key):
                self.assertEqual(result[key], "")

    def test_no_action_returns_status(self):
        with patch.object(self.helper, "status", return_value={"ok": True}) as status:
            self.assertEqual(self.helper.main([]), {"ok": True})
        status.assert_called_once_with()

    def test_profile_action_passes_an_argument_vector_and_refreshes_status(self):
        with patch.object(self.helper, "profiles", return_value=["turbo-game"]):
            with patch.object(self.helper, "run") as run:
                with patch.object(self.helper, "status", return_value={"active": "turbo-game"}):
                    self.assertEqual(self.helper.main(["profile", "turbo-game"]), {"active": "turbo-game"})
        run.assert_called_once_with("profile", "--set", "turbo-game")

    def test_unknown_and_custom_profiles_cannot_be_applied(self):
        with patch.object(self.helper, "profiles", return_value=["quiet", "custom"]):
            with patch.object(self.helper, "run") as run:
                for mode in ("custom", "missing", "quiet; touch /tmp/unwanted"):
                    with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "Invalid profile"):
                        self.helper.main(["profile", mode])
        run.assert_not_called()

    def test_lighting_validates_and_passes_exact_arguments(self):
        with patch.object(self.helper, "run") as run:
            result = self.helper.main(["lighting", "all", "static", "aB12fF", "medium", "normal"])
        run.assert_called_once_with("apply", "--device", "all", "--mode", "static", "--color", "aB12fF", "--brightness", "medium", "--speed", "normal")
        self.assertEqual(result, {"ok": True, "message": "Lighting applied"})

    def test_invalid_lighting_fields_never_invoke_z13ctl(self):
        valid = ["lighting", "keyboard", "rainbow", "00ffCC", "high", "fast"]
        invalid = {1: ["mouse", "all;reboot"], 2: ["flash"], 3: ["#00ffCC", "FFFFF", "GGGGGG", "00ffCC\n"], 4: ["100"], 5: ["maximum"]}
        with patch.object(self.helper, "run") as run:
            for index, values in invalid.items():
                for value in values:
                    args = valid.copy()
                    args[index] = value
                    with self.subTest(args=args), self.assertRaisesRegex(ValueError, "Invalid lighting settings"):
                        self.helper.main(args)
        run.assert_not_called()

    def test_unsupported_actions_and_wrong_arity_never_invoke_z13ctl(self):
        with patch.object(self.helper, "run") as run:
            for args in (["unknown"], ["profile"], ["profile", "quiet", "extra"], ["lighting"], ["lighting", "all", "static", "000000", "high", "fast", "extra"]):
                with self.subTest(args=args), self.assertRaisesRegex(ValueError, "Unsupported command"):
                    self.helper.main(args)
        run.assert_not_called()

    def test_run_strips_output_and_uses_bounded_non_shell_subprocess(self):
        with patch.object(self.helper.subprocess, "run", return_value=completed("  quiet\n")) as run:
            self.assertEqual(self.helper.run("profile", "--get"), "quiet")
        run.assert_called_once_with(["z13ctl", "profile", "--get"], capture_output=True, text=True, timeout=12)

    def test_run_reports_bounded_stderr_or_stdout_on_failure(self):
        for stderr, stdout, expected in (("x" * 400, "fallback", "x" * 300), ("", "  fallback\n", "fallback")):
            with self.subTest(stderr=bool(stderr)):
                with patch.object(self.helper.subprocess, "run", return_value=completed(stdout, stderr, 1)):
                    with self.assertRaises(RuntimeError) as error:
                        self.helper.run("status")
                self.assertEqual(str(error.exception), expected)


class GamingProfileAndLaunchTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper("gaming")

    def test_profile_parsing_deduplicates_and_excludes_manual_custom_state(self):
        with patch.object(self.helper.subprocess, "run", return_value=completed(PROFILE_OUTPUT)) as run:
            self.assertEqual(self.helper.profiles(), ["quiet", "balanced", "performance", "turbo-game", "eco-2"])
        run.assert_called_once_with(["z13ctl", "profile", "--list"], capture_output=True, text=True, timeout=12)

    def test_profile_list_failure_is_reported(self):
        with patch.object(self.helper.subprocess, "run", return_value=completed(returncode=1)):
            with self.assertRaisesRegex(RuntimeError, "Could not read profiles"):
                self.helper.profiles()

    def test_details_parse_descriptions_and_fail_to_empty_mapping(self):
        with patch.object(self.helper.subprocess, "run", return_value=completed(PROFILE_OUTPUT)):
            self.assertEqual(self.helper.profile_details()["turbo-game"], "Updated description")
        with patch.object(self.helper.subprocess, "run", return_value=completed(returncode=1)):
            self.assertEqual(self.helper.profile_details(), {})

    def test_invalid_launch_profile_does_not_probe_or_start_session(self):
        with patch.object(self.helper, "profiles", return_value=["quiet"]):
            with patch.object(self.helper.shutil, "which") as which, patch.object(self.helper.subprocess, "run") as run, patch.object(self.helper.subprocess, "Popen") as popen:
                with self.assertRaisesRegex(ValueError, "Profile unavailable"):
                    self.helper.launch("quiet;reboot")
        which.assert_not_called()
        run.assert_not_called()
        popen.assert_not_called()

    def test_missing_session_selector_prevents_profile_mutation(self):
        with patch.object(self.helper, "profiles", return_value=["quiet"]):
            with patch.object(self.helper.shutil, "which", return_value=None) as which, patch.object(self.helper.subprocess, "run") as run, patch.object(self.helper.subprocess, "Popen") as popen:
                with self.assertRaisesRegex(RuntimeError, "steamos-session-select missing; no session change made"):
                    self.helper.launch("quiet")
        which.assert_called_once_with("steamos-session-select")
        run.assert_not_called()
        popen.assert_not_called()

    def test_missing_z13ctl_prevents_session_launch(self):
        with patch.object(self.helper.subprocess, "run", side_effect=FileNotFoundError("z13ctl")), patch.object(self.helper.subprocess, "Popen") as popen:
            with self.assertRaises(FileNotFoundError):
                self.helper.launch("quiet")
        popen.assert_not_called()

    def test_failed_profile_switch_prevents_session_launch(self):
        with patch.object(self.helper, "profiles", return_value=["quiet"]), patch.object(self.helper.shutil, "which", return_value="/usr/bin/steamos-session-select"):
            with patch.object(self.helper.subprocess, "run", return_value=completed(stderr="denied", returncode=1)) as run, patch.object(self.helper.subprocess, "Popen") as popen:
                with self.assertRaisesRegex(RuntimeError, "Profile switch failed: denied"):
                    self.helper.launch("quiet")
        self.assertEqual(run.call_count, 1)
        popen.assert_not_called()

    def test_unconfirmed_profile_prevents_session_launch(self):
        for active in (completed("performance"), completed("quiet", returncode=1)):
            with self.subTest(active=active.stdout, code=active.returncode):
                with patch.object(self.helper, "profiles", return_value=["quiet"]), patch.object(self.helper.shutil, "which", return_value="/usr/bin/steamos-session-select"):
                    with patch.object(self.helper.subprocess, "run", side_effect=[completed(), active]), patch.object(self.helper.subprocess, "Popen") as popen:
                        with self.assertRaisesRegex(RuntimeError, "Profile not confirmed; Gaming Mode not launched"):
                            self.helper.launch("quiet")
                popen.assert_not_called()

    def test_confirmed_profile_launches_detached_gamescope_session(self):
        with patch.object(self.helper, "profiles", return_value=["quiet"]), patch.object(self.helper.shutil, "which", return_value="/usr/bin/steamos-session-select"):
            with patch.object(self.helper.subprocess, "run", side_effect=[completed(), completed("quiet\n")]) as run, patch.object(self.helper.subprocess, "Popen") as popen:
                result = self.helper.launch("quiet")
        self.assertEqual(run.call_args_list, [
            call(["z13ctl", "profile", "--set", "quiet"], capture_output=True, text=True, timeout=20),
            call(["z13ctl", "profile", "--get"], capture_output=True, text=True, timeout=12),
        ])
        popen.assert_called_once_with(["steamos-session-select", "gamescope"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.assertEqual(result, {"ok": True, "message": "Switching to Gaming Mode: quiet"})

    @unittest.expectedFailure
    def test_known_issue_profile_confirmation_requires_exact_name(self):
        # Baseline launch() uses a substring check: "quiet" matches "quiet-extra".
        with patch.object(self.helper, "profiles", return_value=["quiet"]), patch.object(self.helper.shutil, "which", return_value="/usr/bin/steamos-session-select"):
            with patch.object(self.helper.subprocess, "run", side_effect=[completed(), completed("quiet-extra")]), patch.object(self.helper.subprocess, "Popen"):
                with self.assertRaisesRegex(RuntimeError, "Profile not confirmed"):
                    self.helper.launch("quiet")


if __name__ == "__main__":
    unittest.main()
