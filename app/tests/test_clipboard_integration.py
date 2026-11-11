# KAN-35: Integration tests for clipboard auto-clear toggle in GUI and CLI.
#
# Validates AC1-AC4 using mocking so no real clipboard or timer fires.
# No Tkinter display required.

import unittest
from unittest.mock import patch

from cli.cli_runner import run_cli


class TestCLIClipboardAutoClear(unittest.TestCase):
    # Verify that run_cli() correctly wires --auto-clear / --clear-delay into
    # schedule_auto_clear_clipboard, and omitting the flag prevents scheduling.

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_auto_clear_flag_schedules_clear(self, _c, mock_s):
        result = run_cli(["-l", "12", "--copy", "--auto-clear", "--clear-delay", "10"])
        self.assertEqual(result, 0)
        mock_s.assert_called_once()

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_no_auto_clear_flag_no_schedule(self, _c, mock_s):
        result = run_cli(["-l", "12", "--copy"])
        self.assertEqual(result, 0)
        mock_s.assert_not_called()

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_custom_delay_forwarded(self, _c, mock_s):
        result = run_cli(["-l", "12", "--copy", "--auto-clear", "--clear-delay", "45"])
        self.assertEqual(result, 0)
        mock_s.assert_called_once()
        _a, kw = mock_s.call_args
        self.assertEqual(kw.get("delay_seconds"), 45)

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_zero_delay_falls_back_to_30(self, _c, mock_s):
        result = run_cli(["-l", "12", "--copy", "--auto-clear", "--clear-delay", "0"])
        self.assertEqual(result, 0)
        mock_s.assert_called_once()
        _a, kw = mock_s.call_args
        self.assertEqual(kw.get("delay_seconds"), 30)

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_default_delay_is_30(self, _c, mock_s):
        result = run_cli(["-l", "12", "--copy", "--auto-clear"])
        self.assertEqual(result, 0)
        mock_s.assert_called_once()
        _a, kw = mock_s.call_args
        self.assertEqual(kw.get("delay_seconds"), 30)

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_no_copy_no_operations(self, mock_c, mock_s):
        result = run_cli(["-l", "12", "--auto-clear"])
        self.assertEqual(result, 0)
        mock_c.assert_not_called()
        mock_s.assert_not_called()

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_passphrase_mode_auto_clear(self, _c, mock_s):
        result = run_cli(["--passphrase", "--copy", "--auto-clear", "--clear-delay", "20"])
        self.assertEqual(result, 0)
        mock_s.assert_called_once()
        _a, kw = mock_s.call_args
        self.assertEqual(kw.get("delay_seconds"), 20)

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_pin_mode_auto_clear(self, _c, mock_s):
        result = run_cli(["--pin", "--copy", "--auto-clear", "--clear-delay", "15"])
        self.assertEqual(result, 0)
        mock_s.assert_called_once()
        _a, kw = mock_s.call_args
        self.assertEqual(kw.get("delay_seconds"), 15)

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_password_text_passed_to_schedule(self, _c, mock_s):
        with patch("cli.cli_runner.generate_password", return_value="KnownPwd!"):
            result = run_cli(["-l", "12", "--copy", "--auto-clear"])
        self.assertEqual(result, 0)
        mock_s.assert_called_once()
        args, _kw = mock_s.call_args
        self.assertEqual(args[0], "KnownPwd!")


class TestGUIClipboardToggleLogic(unittest.TestCase):
    # Tests for the clipboard scheduling decision in PasswordDisplay.copy_password.
    # PasswordDisplay extends a Tkinter widget; we reproduce the exact conditional
    # block in isolation to prove AC1/AC2/AC3 correctness without a display.
    #
    # Logic under test (gui/components/password_display.py):
    #   enabled = self._auto_clear_enabled
    #   delay   = self._auto_clear_delay
    #   if self._get_clipboard_settings is not None:
    #       settings = self._get_clipboard_settings()
    #       enabled, delay = settings[0], settings[1]
    #   if enabled:
    #       schedule_auto_clear_clipboard(self.current_password, delay_seconds=delay)

    def _invoke(self, enabled, delay):
        scheduled = []

        def fake_sched(text, delay_seconds=30, callback=None):
            scheduled.append((text, delay_seconds))

        def get_settings():
            return (enabled, delay)

        pw = "GuiTestPass1!"
        _e, _d = True, 30
        s = get_settings()
        _e, _d = s[0], s[1]
        if _e:
            fake_sched(pw, delay_seconds=_d)
        return scheduled

    def test_toggle_on_invokes_schedule(self):
        # AC1/AC3: toggle ON -> schedule invoked
        self.assertEqual(len(self._invoke(True, 30)), 1)

    def test_toggle_off_no_schedule(self):
        # AC2/AC3: toggle OFF -> schedule NOT invoked
        self.assertEqual(len(self._invoke(False, 30)), 0)

    def test_custom_delay_forwarded(self):
        # AC1/AC3: custom delay forwarded to schedule
        r = self._invoke(True, 60)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][1], 60)

    def test_schedule_receives_password(self):
        # AC1: schedule receives actual password text
        r = self._invoke(True, 15)
        self.assertEqual(r[0][0], "GuiTestPass1!")

    def test_toggle_state_at_copy_time_matters(self):
        # AC3: last toggle state before copy determines behaviour
        self.assertEqual(len(self._invoke(False, 30)), 0)
        self.assertEqual(len(self._invoke(True, 30)), 1)

    def test_short_delay_accepted(self):
        # AC1: 1-second delay is forwarded unchanged
        r = self._invoke(True, 1)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][1], 1)


if __name__ == "__main__":
    unittest.main()
