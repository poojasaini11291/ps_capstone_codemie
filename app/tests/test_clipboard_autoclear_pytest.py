"""
Pytest-based integration tests for the clipboard auto-clear feature
(KAN-9/KAN-10/KAN-11).

Unlike test_clipboard.py, these drive the real public API
(copy_with_autoclear) against real threading.Timer instances with short
real delays, instead of injecting a synchronous schedule_fn. They exist to
verify the actual wall-clock behaviour end-to-end, since this is a desktop
app with no browser surface for Playwright.
"""
import time

import pytest

from core import clipboard


class FakeSystemClipboard:
    """In-memory stand-in for the OS clipboard so tests never touch the real one."""

    def __init__(self):
        self.value = ""

    def copy(self, text):
        self.value = text

    def paste(self):
        return self.value


@pytest.fixture
def fake_clipboard(monkeypatch):
    import pyperclip

    board = FakeSystemClipboard()
    monkeypatch.setattr(pyperclip, "copy", board.copy)
    monkeypatch.setattr(pyperclip, "paste", board.paste)
    return board


@pytest.fixture(autouse=True)
def reset_autoclear_settings():
    clipboard.set_autoclear_enabled(True)
    clipboard.set_autoclear_delay(clipboard.DEFAULT_AUTOCLEAR_SECONDS)
    yield
    clipboard.set_autoclear_enabled(True)
    clipboard.set_autoclear_delay(clipboard.DEFAULT_AUTOCLEAR_SECONDS)


def _wait_until(predicate, timeout=2.0, interval=0.01):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


def test_copy_with_autoclear_puts_password_on_clipboard(fake_clipboard):
    """AC1: copying writes the password to the clipboard and reports success."""
    result = clipboard.copy_with_autoclear("hunter2")

    assert result is True
    assert fake_clipboard.paste() == "hunter2"


def test_clipboard_clears_itself_after_real_timeout(fake_clipboard):
    """AC2: once the configured timeout really elapses, the clipboard clears.

    Uses schedule_auto_clear_clipboard directly (rather than
    copy_with_autoclear + set_autoclear_delay) because set_autoclear_delay
    truncates to whole seconds, and a real 30s wait is not practical here.
    """
    fake_clipboard.copy("hunter2")

    clipboard.schedule_auto_clear_clipboard(
        "hunter2",
        delay_seconds=0.1,
        clipboard_get=fake_clipboard.paste,
        clipboard_set=fake_clipboard.copy,
    )

    assert fake_clipboard.paste() == "hunter2"
    assert _wait_until(lambda: fake_clipboard.paste() == "")


def test_second_copy_before_timeout_resets_the_clear_countdown(fake_clipboard):
    """AC3: a second copy cancels the first pending clear and restarts the
    countdown from the newest copy, instead of clearing on the old schedule."""
    fake_clipboard.copy("secret1")
    clipboard.schedule_auto_clear_clipboard(
        "secret1",
        delay_seconds=0.6,
        clipboard_get=fake_clipboard.paste,
        clipboard_set=fake_clipboard.copy,
    )

    time.sleep(0.3)
    fake_clipboard.copy("secret2")
    clipboard.schedule_auto_clear_clipboard(
        "secret2",
        delay_seconds=0.6,
        clipboard_get=fake_clipboard.paste,
        clipboard_set=fake_clipboard.copy,
    )

    # secret1's original 0.6s window has now elapsed, but its clear was
    # superseded, so secret2 must still be on the clipboard.
    time.sleep(0.45)
    assert fake_clipboard.paste() == "secret2"

    # secret2's own 0.6s window (started at the second copy) has now elapsed.
    assert _wait_until(lambda: fake_clipboard.paste() == "")


def test_disabling_autoclear_leaves_password_on_clipboard(fake_clipboard):
    """AC4: disabling auto-clear leaves the copied password on the clipboard."""
    clipboard.set_autoclear_delay(0.1)
    clipboard.set_autoclear_enabled(False)

    clipboard.copy_with_autoclear("hunter2")
    time.sleep(0.2)

    assert fake_clipboard.paste() == "hunter2"
