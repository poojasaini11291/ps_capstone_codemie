"""
Unit tests for clipboard auto-clear (KAN-18).

Uses mock threading.Timer to avoid real sleeps; never touches the real
system clipboard. Covers:
  - Copy triggers clipboard write and starts a clear timer.
  - Repeated copy cancels the prior timer and only clears once after the
    latest delay.
  - Unsupported/failed clear path is handled gracefully (no raise) and
    on_clear_failed callback is invoked.
"""
import threading
import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import core.clipboard as clipboard_module
from core.clipboard import (
    copy_to_clipboard,
    schedule_auto_clear_clipboard,
    CLIPBOARD_CLEAR_TIMEOUT_SECS,
)


def _reset_timer():
    if clipboard_module._auto_clear_timer is not None:
        clipboard_module._auto_clear_timer.cancel()
        clipboard_module._auto_clear_timer = None


class TestClipboardConstant(unittest.TestCase):
    def test_default_timeout_is_30(self):
        self.assertEqual(CLIPBOARD_CLEAR_TIMEOUT_SECS, 30)


class TestScheduleAutoClear(unittest.TestCase):
    def setUp(self):
        _reset_timer()

    def tearDown(self):
        _reset_timer()

    # ------------------------------------------------------------------
    # AC1-adjacent: copy triggers timer
    # ------------------------------------------------------------------
    @patch("core.clipboard.threading.Timer")
    def test_copy_starts_timer(self, mock_timer_cls):
        """Calling schedule_auto_clear_clipboard creates and starts a Timer."""
        mock_timer = MagicMock()
        mock_timer_cls.return_value = mock_timer

        schedule_auto_clear_clipboard("secret")

        mock_timer_cls.assert_called_once()
        delay_arg = mock_timer_cls.call_args[0][0]
        self.assertEqual(delay_arg, CLIPBOARD_CLEAR_TIMEOUT_SECS)
        mock_timer.start.assert_called_once()

    @patch("core.clipboard.threading.Timer")
    def test_timer_is_daemon(self, mock_timer_cls):
        mock_timer = MagicMock()
        mock_timer_cls.return_value = mock_timer
        schedule_auto_clear_clipboard("secret")
        self.assertTrue(mock_timer.daemon)

    # ------------------------------------------------------------------
    # AC2: clear fires after timeout if clipboard unchanged
    # ------------------------------------------------------------------
    @patch("core.clipboard.threading.Timer")
    def test_clear_fires_when_clipboard_still_matches(self, mock_timer_cls):
        """After the delay, if clipboard still holds the copied text it is cleared."""
        fire_fn = None

        def capture(delay, fn):
            nonlocal fire_fn
            fire_fn = fn
            return MagicMock()

        mock_timer_cls.side_effect = capture

        with patch("pyperclip.paste", return_value="secret"), \
             patch("pyperclip.copy") as mock_copy:
            schedule_auto_clear_clipboard("secret")
            fire_fn()

        mock_copy.assert_called_once_with("")

    @patch("core.clipboard.threading.Timer")
    def test_clear_skips_when_clipboard_changed(self, mock_timer_cls):
        """Clear does NOT run if clipboard no longer holds the copied value."""
        fire_fn = None

        def capture(delay, fn):
            nonlocal fire_fn
            fire_fn = fn
            return MagicMock()

        mock_timer_cls.side_effect = capture

        with patch("pyperclip.paste", return_value="something_else"), \
             patch("pyperclip.copy") as mock_copy:
            schedule_auto_clear_clipboard("secret")
            fire_fn()

        mock_copy.assert_not_called()

    # ------------------------------------------------------------------
    # AC3: repeated copy cancels prior timer, only latest clear runs
    # ------------------------------------------------------------------
    @patch("core.clipboard.threading.Timer")
    def test_recopy_cancels_first_timer_and_starts_new_one(self, mock_timer_cls):
        """A second copy before timeout: first timer is cancelled, second is started."""
        timers = []

        def make_timer(delay, fn):
            t = MagicMock()
            t.daemon = False
            timers.append(t)
            return t

        mock_timer_cls.side_effect = make_timer

        schedule_auto_clear_clipboard("first")
        first = timers[0]

        schedule_auto_clear_clipboard("second")
        second = timers[1]

        first.cancel.assert_called_once()
        second.cancel.assert_not_called()
        second.start.assert_called_once()

    @patch("core.clipboard.threading.Timer")
    def test_only_latest_copy_clears(self, mock_timer_cls):
        """Only the most-recent copy's fn clears; the stale fn sees different clipboard."""
        fns = []

        def capture(delay, fn):
            fns.append(fn)
            t = MagicMock()
            t.daemon = False
            return t

        mock_timer_cls.side_effect = capture

        schedule_auto_clear_clipboard("first")
        schedule_auto_clear_clipboard("second")

        # Simulate first fn fires (clipboard has "second" now — should not clear)
        with patch("pyperclip.paste", return_value="second"), \
             patch("pyperclip.copy") as mock_copy:
            fns[0]()
        mock_copy.assert_not_called()

        # Simulate second fn fires (clipboard still has "second" — should clear)
        with patch("pyperclip.paste", return_value="second"), \
             patch("pyperclip.copy") as mock_copy:
            fns[1]()
        mock_copy.assert_called_once_with("")

    # ------------------------------------------------------------------
    # AC4: unsupported environment handled gracefully
    # ------------------------------------------------------------------
    @patch("core.clipboard.threading.Timer")
    def test_clear_failure_calls_on_clear_failed_not_raise(self, mock_timer_cls):
        """If clipboard clear raises, on_clear_failed is called and no exception propagates."""
        fire_fn = None

        def capture(delay, fn):
            nonlocal fire_fn
            fire_fn = fn
            return MagicMock()

        mock_timer_cls.side_effect = capture
        err_cb = MagicMock()

        err = RuntimeError("clipboard not available")
        with patch("pyperclip.paste", side_effect=err):
            schedule_auto_clear_clipboard("secret", on_clear_failed=err_cb)
            fire_fn()  # must not raise

        err_cb.assert_called_once_with(err)

    @patch("core.clipboard.threading.Timer")
    def test_clear_failure_without_callback_does_not_raise(self, mock_timer_cls):
        """If clipboard clear raises and no on_clear_failed is set, no exception propagates."""
        fire_fn = None

        def capture(delay, fn):
            nonlocal fire_fn
            fire_fn = fn
            return MagicMock()

        mock_timer_cls.side_effect = capture

        with patch("pyperclip.paste", side_effect=RuntimeError("no clipboard")):
            schedule_auto_clear_clipboard("secret")
            fire_fn()  # must not raise


class TestCopyToClipboard(unittest.TestCase):
    def setUp(self):
        _reset_timer()

    def tearDown(self):
        _reset_timer()

    def test_returns_false_for_empty_string(self):
        self.assertFalse(copy_to_clipboard(""))

    def test_returns_false_for_none(self):
        self.assertFalse(copy_to_clipboard(None))

    @patch("pyperclip.copy")
    def test_returns_true_on_pyperclip_success(self, mock_copy):
        result = copy_to_clipboard("test-password")
        self.assertTrue(result)
        mock_copy.assert_called_once_with("test-password")

    @patch("pyperclip.copy", side_effect=Exception("no clipboard"))
    @patch("tkinter.Tk", side_effect=Exception("no display"))
    def test_returns_false_when_both_backends_fail(self, _tk, _pc):
        result = copy_to_clipboard("test")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
