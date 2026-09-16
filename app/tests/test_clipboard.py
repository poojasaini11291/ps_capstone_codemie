import unittest
from unittest.mock import Mock, patch

from core import clipboard


class TestClipboardSettings(unittest.TestCase):

    def setUp(self):
        clipboard.set_autoclear_enabled(True)
        clipboard.set_autoclear_delay(clipboard.DEFAULT_AUTOCLEAR_SECONDS)

    def test_default_settings(self):
        self.assertTrue(clipboard.get_autoclear_enabled())
        self.assertEqual(clipboard.get_autoclear_delay(), clipboard.DEFAULT_AUTOCLEAR_SECONDS)

    def test_set_autoclear_enabled(self):
        clipboard.set_autoclear_enabled(False)
        self.assertFalse(clipboard.get_autoclear_enabled())

    def test_set_autoclear_delay_rejects_negative(self):
        clipboard.set_autoclear_delay(-5)
        self.assertEqual(clipboard.get_autoclear_delay(), 0)


class TestCopyToClipboard(unittest.TestCase):

    def test_empty_text_returns_false(self):
        self.assertFalse(clipboard.copy_to_clipboard(""))

    @patch("pyperclip.copy")
    def test_copies_via_pyperclip(self, mock_copy):
        result = clipboard.copy_to_clipboard("hunter2")
        self.assertTrue(result)
        mock_copy.assert_called_once_with("hunter2")

    @patch("tkinter.Tk", side_effect=RuntimeError("no display"))
    @patch("pyperclip.copy", side_effect=RuntimeError("no clipboard provider"))
    def test_logs_warning_and_returns_false_when_all_backends_fail(self, mock_pyperclip, mock_tk):
        with self.assertLogs(clipboard.logger.name, level="WARNING") as log_ctx:
            result = clipboard.copy_to_clipboard("hunter2")

        self.assertFalse(result)
        self.assertTrue(any("Clipboard is unavailable" in msg for msg in log_ctx.output))


class TestScheduleAutoClearClipboard(unittest.TestCase):

    @staticmethod
    def _immediate_schedule(delay_seconds, fn):
        fn()
        return Mock()

    def test_clears_when_clipboard_still_matches(self):
        clipboard_get = Mock(return_value="secret123")
        clipboard_set = Mock()
        callback = Mock()

        clipboard.schedule_auto_clear_clipboard(
            "secret123",
            delay_seconds=5,
            callback=callback,
            clipboard_get=clipboard_get,
            clipboard_set=clipboard_set,
            schedule_fn=self._immediate_schedule,
        )

        clipboard_set.assert_called_once_with("")
        callback.assert_called_once()

    def test_does_not_clear_when_clipboard_changed(self):
        clipboard_get = Mock(return_value="something-else")
        clipboard_set = Mock()

        clipboard.schedule_auto_clear_clipboard(
            "secret123",
            delay_seconds=5,
            clipboard_get=clipboard_get,
            clipboard_set=clipboard_set,
            schedule_fn=self._immediate_schedule,
        )

        clipboard_set.assert_not_called()

    def test_newer_copy_supersedes_older_pending_clear(self):
        fired = []

        def capture_schedule(delay_seconds, fn):
            fired.append(fn)
            return Mock()

        clipboard_get = Mock(return_value="secret2")
        clipboard_set = Mock()

        clipboard.schedule_auto_clear_clipboard(
            "secret1", delay_seconds=5,
            clipboard_get=clipboard_get, clipboard_set=clipboard_set,
            schedule_fn=capture_schedule,
        )
        clipboard.schedule_auto_clear_clipboard(
            "secret2", delay_seconds=5,
            clipboard_get=clipboard_get, clipboard_set=clipboard_set,
            schedule_fn=capture_schedule,
        )

        # The stale (first) timer firing late must be a no-op.
        fired[0]()
        clipboard_set.assert_not_called()

        # The current (second) timer firing performs the clear.
        fired[1]()
        clipboard_set.assert_called_once_with("")

    def test_logs_warning_when_clear_fails(self):
        clipboard_get = Mock(side_effect=RuntimeError("clipboard provider gone"))
        clipboard_set = Mock()

        with self.assertLogs(clipboard.logger.name, level="WARNING") as log_ctx:
            clipboard.schedule_auto_clear_clipboard(
                "secret123",
                delay_seconds=5,
                clipboard_get=clipboard_get,
                clipboard_set=clipboard_set,
                schedule_fn=self._immediate_schedule,
            )

        clipboard_set.assert_not_called()
        self.assertTrue(any("auto-clear failed" in msg for msg in log_ctx.output))

    def test_uses_configured_default_delay_when_not_specified(self):
        clipboard.set_autoclear_delay(42)
        seen_delay = {}

        def capture_delay(delay_seconds, fn):
            seen_delay["value"] = delay_seconds
            fn()
            return Mock()

        clipboard.schedule_auto_clear_clipboard(
            "secret", clipboard_get=Mock(return_value="secret"),
            clipboard_set=Mock(), schedule_fn=capture_delay,
        )

        self.assertEqual(seen_delay["value"], 42)
        clipboard.set_autoclear_delay(clipboard.DEFAULT_AUTOCLEAR_SECONDS)


class TestCopyWithAutoclear(unittest.TestCase):

    def setUp(self):
        clipboard.set_autoclear_enabled(True)
        clipboard.set_autoclear_delay(clipboard.DEFAULT_AUTOCLEAR_SECONDS)

    @patch("core.clipboard.schedule_auto_clear_clipboard")
    @patch("core.clipboard.copy_to_clipboard", return_value=True)
    def test_copies_immediately_and_schedules_when_enabled(self, mock_copy, mock_schedule):
        result = clipboard.copy_with_autoclear("s3cret")

        self.assertTrue(result)
        mock_copy.assert_called_once_with("s3cret", root_window=None)
        mock_schedule.assert_called_once_with("s3cret")

    @patch("core.clipboard.schedule_auto_clear_clipboard")
    @patch("core.clipboard.copy_to_clipboard", return_value=True)
    def test_does_not_schedule_when_disabled(self, mock_copy, mock_schedule):
        clipboard.set_autoclear_enabled(False)

        result = clipboard.copy_with_autoclear("s3cret")

        self.assertTrue(result)
        mock_schedule.assert_not_called()

    @patch("core.clipboard.schedule_auto_clear_clipboard")
    @patch("core.clipboard.copy_to_clipboard", return_value=True)
    def test_does_not_schedule_when_delay_is_zero(self, mock_copy, mock_schedule):
        clipboard.set_autoclear_delay(0)

        clipboard.copy_with_autoclear("s3cret")

        mock_schedule.assert_not_called()

    @patch("core.clipboard.schedule_auto_clear_clipboard")
    @patch("core.clipboard.copy_to_clipboard", return_value=False)
    def test_does_not_schedule_when_copy_fails(self, mock_copy, mock_schedule):
        result = clipboard.copy_with_autoclear("s3cret")

        self.assertFalse(result)
        mock_schedule.assert_not_called()


if __name__ == "__main__":
    unittest.main()
