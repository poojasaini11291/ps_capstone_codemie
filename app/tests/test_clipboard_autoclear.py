import time
import unittest
from unittest.mock import patch, MagicMock


class TestClipboardAutoClearScheduling(unittest.TestCase):
    """Tests for clipboard auto-clear with timer reset (KAN-16)."""

    def setUp(self):
        import core.clipboard as cb_mod
        cb_mod._cancel_event = None

    @patch("core.clipboard.threading.Thread")
    def test_successful_copy_schedules_clear(self, mock_thread_cls):
        """AC1: Successful copy schedules a delayed clipboard clear."""
        from core.clipboard import schedule_auto_clear_clipboard

        mock_inst = MagicMock()
        mock_thread_cls.return_value = mock_inst

        schedule_auto_clear_clipboard("secret", delay_seconds=30)

        mock_thread_cls.assert_called_once()
        _, kwargs = mock_thread_cls.call_args
        self.assertTrue(kwargs.get("daemon", False))
        mock_inst.start.assert_called_once()

    def test_second_copy_resets_timer(self):
        """AC3: Second copy cancels the first timer so only the latest clear fires."""
        from core.clipboard import schedule_auto_clear_clipboard
        import core.clipboard as cb_mod

        schedule_auto_clear_clipboard("first", delay_seconds=60)
        first_event = cb_mod._cancel_event
        self.assertIsNotNone(first_event)
        self.assertFalse(first_event.is_set(), "First event should not be cancelled yet")

        schedule_auto_clear_clipboard("second", delay_seconds=60)
        self.assertTrue(first_event.is_set(), "First event should be cancelled after second copy")
        second_event = cb_mod._cancel_event
        self.assertIsNotNone(second_event)
        self.assertFalse(second_event.is_set(), "Second event should not yet be cancelled")

    @patch("pyperclip.copy")
    @patch("pyperclip.paste", side_effect=Exception("clipboard unavailable"))
    def test_clear_failure_does_not_crash(self, mock_paste, mock_copy):
        """AC4: Exception from clipboard API is swallowed; app does not crash."""
        from core.clipboard import schedule_auto_clear_clipboard

        schedule_auto_clear_clipboard("secret", delay_seconds=0)
        time.sleep(0.15)

        mock_paste.assert_called()
        mock_copy.assert_not_called()

    @patch("pyperclip.copy")
    @patch("pyperclip.paste", return_value="secret")
    def test_clear_overwrites_clipboard_with_empty_string(self, mock_paste, mock_copy):
        """AC2: After delay, clipboard is overwritten with empty string."""
        from core.clipboard import schedule_auto_clear_clipboard

        schedule_auto_clear_clipboard("secret", delay_seconds=0)
        time.sleep(0.15)

        mock_copy.assert_called_once_with("")


if __name__ == "__main__":
    unittest.main()
