import threading
import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import core.clipboard as clipboard_module
from core.clipboard import copy_to_clipboard, schedule_auto_clear_clipboard


class TestScheduleAutoClearClipboard(unittest.TestCase):
    """Tests for schedule_auto_clear_clipboard using fake/mock timers."""

    def setUp(self):
        # Reset module-level timer before each test
        if clipboard_module._auto_clear_timer is not None:
            clipboard_module._auto_clear_timer.cancel()
            clipboard_module._auto_clear_timer = None

    def tearDown(self):
        if clipboard_module._auto_clear_timer is not None:
            clipboard_module._auto_clear_timer.cancel()
            clipboard_module._auto_clear_timer = None

    @patch("core.clipboard.threading.Timer")
    def test_schedules_timer_when_called(self, mock_timer_cls):
        """Enabled: calling schedule_auto_clear_clipboard creates and starts a Timer."""
        mock_timer = MagicMock()
        mock_timer_cls.return_value = mock_timer

        schedule_auto_clear_clipboard("secret", delay_seconds=30)

        mock_timer_cls.assert_called_once()
        args = mock_timer_cls.call_args
        self.assertEqual(args[0][0], 30)
        mock_timer.start.assert_called_once()

    @patch("core.clipboard.threading.Timer")
    def test_timer_is_daemon(self, mock_timer_cls):
        """Timer is created as a daemon so it does not block app exit."""
        mock_timer = MagicMock()
        mock_timer_cls.return_value = mock_timer

        schedule_auto_clear_clipboard("secret", delay_seconds=5)

        self.assertTrue(mock_timer.daemon)

    @patch("core.clipboard.threading.Timer")
    def test_clear_executes_when_clipboard_matches(self, mock_timer_cls):
        """The clear callback clears clipboard when it still holds the copied text."""
        fired_fn = None

        def capture_timer(delay, fn):
            nonlocal fired_fn
            fired_fn = fn
            t = MagicMock()
            t.daemon = False
            return t

        mock_timer_cls.side_effect = capture_timer

        with patch("pyperclip.paste", return_value="secret"), \
             patch("pyperclip.copy") as mock_copy:
            schedule_auto_clear_clipboard("secret", delay_seconds=5)
            fired_fn()  # simulate timer firing

        mock_copy.assert_called_once_with("")

    @patch("core.clipboard.threading.Timer")
    def test_clear_skips_when_clipboard_changed(self, mock_timer_cls):
        """The clear callback does nothing if clipboard content has changed."""
        fired_fn = None

        def capture_timer(delay, fn):
            nonlocal fired_fn
            fired_fn = fn
            return MagicMock()

        mock_timer_cls.side_effect = capture_timer

        with patch("pyperclip.paste", return_value="different_content"), \
             patch("pyperclip.copy") as mock_copy:
            schedule_auto_clear_clipboard("secret", delay_seconds=5)
            fired_fn()

        mock_copy.assert_not_called()

    @patch("core.clipboard.threading.Timer")
    def test_callback_invoked_after_clear(self, mock_timer_cls):
        """Optional callback is called after clipboard is cleared."""
        fired_fn = None

        def capture_timer(delay, fn):
            nonlocal fired_fn
            fired_fn = fn
            return MagicMock()

        mock_timer_cls.side_effect = capture_timer
        cb = MagicMock()

        with patch("pyperclip.paste", return_value="secret"), \
             patch("pyperclip.copy"):
            schedule_auto_clear_clipboard("secret", delay_seconds=5, callback=cb)
            fired_fn()

        cb.assert_called_once()

    @patch("core.clipboard.threading.Timer")
    def test_recopy_cancels_previous_timer(self, mock_timer_cls):
        """Re-copy before timeout: prior scheduled clear is cancelled; only latest timer runs."""
        timers = []

        def make_timer(delay, fn):
            t = MagicMock()
            t.daemon = False
            timers.append(t)
            return t

        mock_timer_cls.side_effect = make_timer

        schedule_auto_clear_clipboard("first", delay_seconds=30)
        self.assertEqual(len(timers), 1)
        first_timer = timers[0]

        schedule_auto_clear_clipboard("second", delay_seconds=30)
        self.assertEqual(len(timers), 2)

        # First timer must have been cancelled when the second copy happened
        first_timer.cancel.assert_called_once()
        # Second timer is started, not cancelled
        timers[1].cancel.assert_not_called()
        timers[1].start.assert_called_once()

    @patch("core.clipboard.threading.Timer")
    def test_no_scheduling_when_not_called(self, mock_timer_cls):
        """Disabled: if schedule_auto_clear_clipboard is not called, no timer is created."""
        # Simply never calling the function means no timer — verify module state is clean
        mock_timer_cls.assert_not_called()
        self.assertIsNone(clipboard_module._auto_clear_timer)


class TestCopyToClipboard(unittest.TestCase):
    """Tests for the base copy_to_clipboard function."""

    def test_returns_false_for_empty_string(self):
        self.assertFalse(copy_to_clipboard(""))

    def test_returns_false_for_none(self):
        self.assertFalse(copy_to_clipboard(None))

    @patch("pyperclip.copy")
    def test_returns_true_on_success(self, mock_copy):
        result = copy_to_clipboard("test-password")
        self.assertTrue(result)
        mock_copy.assert_called_once_with("test-password")

    @patch("pyperclip.copy", side_effect=Exception("no clipboard"))
    @patch("tkinter.Tk", side_effect=Exception("no display"))
    def test_falls_back_gracefully_when_both_backends_fail(self, _tk, _pc):
        # Should not raise; returns False when both pyperclip and tkinter fail
        result = copy_to_clipboard("test")
        self.assertFalse(result)


class TestCLIAutoClear(unittest.TestCase):
    """Tests for CLI auto-clear flag validation."""

    def _run_cli(self, args):
        from cli.cli_runner import run_cli
        return run_cli(args)

    @patch("core.clipboard.threading.Timer")
    @patch("pyperclip.copy")
    @patch("pyperclip.paste", return_value="")
    def test_cli_invalid_seconds_exits_nonzero(self, *_):
        """--auto-clear-seconds 0 should fail with exit code 1."""
        code = self._run_cli(["--copy", "--auto-clear-clipboard", "--auto-clear-seconds", "0"])
        self.assertEqual(code, 1)

    @patch("core.clipboard.threading.Timer")
    @patch("pyperclip.copy")
    @patch("pyperclip.paste", return_value="")
    def test_cli_negative_seconds_exits_nonzero(self, *_):
        """--auto-clear-seconds -5 should fail with exit code 1."""
        code = self._run_cli(["--copy", "--auto-clear-clipboard", "--auto-clear-seconds", "-5"])
        self.assertEqual(code, 1)

    @patch("core.clipboard.schedule_auto_clear_clipboard")
    @patch("pyperclip.copy")
    def test_cli_no_auto_clear_by_default(self, mock_copy, mock_schedule):
        """Without --auto-clear-clipboard, schedule_auto_clear_clipboard is never called."""
        self._run_cli(["--copy"])
        mock_schedule.assert_not_called()

    @patch("core.clipboard.schedule_auto_clear_clipboard")
    @patch("pyperclip.copy")
    def test_cli_auto_clear_schedules_timer(self, mock_copy, mock_schedule):
        """With --auto-clear-clipboard and valid seconds, schedule is called."""
        fake_timer = MagicMock()
        fake_timer.join = MagicMock()
        mock_schedule.return_value = fake_timer

        self._run_cli(["--copy", "--auto-clear-clipboard", "--auto-clear-seconds", "15"])

        mock_schedule.assert_called_once()
        call_args = mock_schedule.call_args
        self.assertEqual(call_args[1]["delay_seconds"], 15)


if __name__ == "__main__":
    unittest.main()
