import unittest
from unittest.mock import patch, MagicMock, call
import threading

import core.clipboard as clipboard_module
from core.clipboard import (
    schedule_auto_clear_clipboard,
    cancel_auto_clear_clipboard,
)


class TestScheduleAutoClipboard(unittest.TestCase):

    def setUp(self):
        # Reset module-level timer before each test
        cancel_auto_clear_clipboard()

    def tearDown(self):
        cancel_auto_clear_clipboard()

    @patch("core.clipboard.threading.Timer")
    def test_default_delay_is_30(self, mock_timer_cls):
        mock_timer = MagicMock()
        mock_timer_cls.return_value = mock_timer

        schedule_auto_clear_clipboard("secret")

        mock_timer_cls.assert_called_once()
        args, _ = mock_timer_cls.call_args
        self.assertEqual(args[0], 30.0)

    @patch("core.clipboard.threading.Timer")
    def test_custom_delay_is_honoured(self, mock_timer_cls):
        mock_timer = MagicMock()
        mock_timer_cls.return_value = mock_timer

        schedule_auto_clear_clipboard("secret", delay_seconds=60)

        args, _ = mock_timer_cls.call_args
        self.assertEqual(args[0], 60.0)

    @patch("core.clipboard.threading.Timer")
    def test_repeated_copy_cancels_previous_timer(self, mock_timer_cls):
        first_timer = MagicMock()
        second_timer = MagicMock()
        mock_timer_cls.side_effect = [first_timer, second_timer]

        schedule_auto_clear_clipboard("pass1")
        schedule_auto_clear_clipboard("pass2")

        first_timer.cancel.assert_called_once()
        second_timer.start.assert_called_once()

    @patch("core.clipboard.threading.Timer")
    def test_no_timer_when_immediately_cancelled(self, mock_timer_cls):
        mock_timer = MagicMock()
        mock_timer_cls.return_value = mock_timer

        schedule_auto_clear_clipboard("secret")
        cancel_auto_clear_clipboard()

        mock_timer.cancel.assert_called_once()
        self.assertIsNone(clipboard_module._active_timer)

    @patch("pyperclip.copy")
    @patch("pyperclip.paste", return_value="secret")
    def test_clears_clipboard_when_value_matches(self, mock_paste, mock_copy):
        fired = threading.Event()
        original_timer = threading.Timer

        def instant_timer(delay, fn):
            t = original_timer(0, fn)
            return t

        with patch("core.clipboard.threading.Timer", side_effect=instant_timer):
            schedule_auto_clear_clipboard("secret", delay_seconds=0)
            # Give the daemon thread a moment to fire
            import time; time.sleep(0.1)

        mock_copy.assert_called_with("")

    @patch("pyperclip.copy")
    @patch("pyperclip.paste", return_value="something_else")
    def test_does_not_clear_when_clipboard_changed(self, mock_paste, mock_copy):
        original_timer = threading.Timer

        def instant_timer(delay, fn):
            return original_timer(0, fn)

        with patch("core.clipboard.threading.Timer", side_effect=instant_timer):
            schedule_auto_clear_clipboard("secret", delay_seconds=0)
            import time; time.sleep(0.1)

        mock_copy.assert_not_called()

    @patch("core.clipboard.threading.Timer")
    def test_timer_is_set_to_daemon(self, mock_timer_cls):
        mock_timer = MagicMock()
        mock_timer_cls.return_value = mock_timer

        schedule_auto_clear_clipboard("secret")

        self.assertTrue(mock_timer.daemon)


if __name__ == "__main__":
    unittest.main()
