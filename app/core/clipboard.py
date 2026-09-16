import logging
import threading
import tkinter as tk
from typing import Optional, Callable

logger = logging.getLogger(__name__)

# Default delay before an auto-scheduled clipboard clear fires. Used by both
# the GUI and CLI unless the user configures a different value.
DEFAULT_AUTOCLEAR_SECONDS = 15

_settings_lock = threading.Lock()
_autoclear_enabled = True
_autoclear_delay_seconds = DEFAULT_AUTOCLEAR_SECONDS

_timer_lock = threading.Lock()
_pending_timer: Optional[threading.Timer] = None
_clear_token = 0


def set_autoclear_enabled(enabled: bool) -> None:
    global _autoclear_enabled
    with _settings_lock:
        _autoclear_enabled = bool(enabled)


def get_autoclear_enabled() -> bool:
    with _settings_lock:
        return _autoclear_enabled


def set_autoclear_delay(seconds: int) -> None:
    global _autoclear_delay_seconds
    with _settings_lock:
        _autoclear_delay_seconds = max(0, int(seconds))


def get_autoclear_delay() -> int:
    with _settings_lock:
        return _autoclear_delay_seconds


def copy_to_clipboard(text: str, root_window: Optional[tk.Tk] = None) -> bool:
    """
    Copies text to the system clipboard using pyperclip or tkinter fallback.
    """
    if not text:
        return False

    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    try:
        if root_window:
            root_window.clipboard_clear()
            root_window.clipboard_append(text)
            root_window.update()
            return True
        else:
            temp_root = tk.Tk()
            temp_root.withdraw()
            temp_root.clipboard_clear()
            temp_root.clipboard_append(text)
            temp_root.update()
            temp_root.destroy()
            return True
    except Exception:
        return False


def _default_clipboard_get() -> str:
    import pyperclip
    return pyperclip.paste()


def _default_clipboard_set(text: str) -> None:
    import pyperclip
    pyperclip.copy(text)


def _default_schedule(delay_seconds: float, fn: Callable[[], None]) -> threading.Timer:
    timer = threading.Timer(delay_seconds, fn)
    timer.daemon = True
    timer.start()
    return timer


def schedule_auto_clear_clipboard(
    copied_text: str,
    delay_seconds: Optional[int] = None,
    callback: Optional[Callable[[], None]] = None,
    clipboard_get: Optional[Callable[[], str]] = None,
    clipboard_set: Optional[Callable[[str], None]] = None,
    schedule_fn: Optional[Callable[[float, Callable[[], None]], threading.Timer]] = None,
) -> threading.Timer:
    """
    Schedules the clipboard to be cleared after delay_seconds, but only if it
    still holds copied_text at fire time (a newer copy is left untouched).

    Only one auto-clear is ever pending: calling this again cancels the
    previous timer so the newest copy wins. clipboard_get/set and schedule_fn
    are injectable so tests can verify behavior without touching the real
    clipboard or sleeping.
    """
    global _pending_timer, _clear_token

    if delay_seconds is None:
        delay_seconds = get_autoclear_delay()

    clipboard_get = clipboard_get or _default_clipboard_get
    clipboard_set = clipboard_set or _default_clipboard_set
    schedule_fn = schedule_fn or _default_schedule

    with _timer_lock:
        if _pending_timer is not None:
            _pending_timer.cancel()
        _clear_token += 1
        token = _clear_token

    def _fire():
        with _timer_lock:
            if token != _clear_token:
                return  # a newer copy superseded this clear
        try:
            if clipboard_get() == copied_text:
                clipboard_set("")
                if callback:
                    callback()
        except Exception as exc:
            logger.debug("Clipboard auto-clear failed: %s", exc)

    timer = schedule_fn(delay_seconds, _fire)

    with _timer_lock:
        _pending_timer = timer

    return timer


def copy_with_autoclear(text: str, root_window: Optional[tk.Tk] = None) -> bool:
    """
    Copies text to the clipboard and, unless auto-clear is disabled or the
    delay is 0, schedules it to be cleared later. Single entry point shared
    by the GUI and CLI so both honor the same configuration.
    """
    success = copy_to_clipboard(text, root_window=root_window)
    if success and get_autoclear_enabled() and get_autoclear_delay() > 0:
        schedule_auto_clear_clipboard(text)
    return success
