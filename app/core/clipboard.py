import threading
import tkinter as tk
from typing import Optional, Callable

# Default auto-clear timeout. Change this constant to adjust the global default.
CLIPBOARD_CLEAR_TIMEOUT_SECS = 30

_auto_clear_timer: Optional[threading.Timer] = None


def copy_to_clipboard(text: str, root_window: Optional[tk.Tk] = None) -> bool:
    """
    Copies text to the system clipboard using pyperclip or tkinter fallback.
    """
    if not text:
        return False

    # Try pyperclip first
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    # Fallback to Tkinter clipboard
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


def schedule_auto_clear_clipboard(
    copied_text: str,
    delay_seconds: int = CLIPBOARD_CLEAR_TIMEOUT_SECS,
    callback: Optional[Callable[[], None]] = None,
    on_clear_failed: Optional[Callable[[Exception], None]] = None,
    root_window: Optional[tk.Tk] = None
) -> threading.Timer:
    """
    Clears the clipboard after delay_seconds if it still contains copied_text.

    Cancels any previously scheduled clear before starting a new timer, so
    repeated copies never accumulate runaway timers. Returns the new Timer so
    callers can join() it when needed (e.g. CLI blocking wait).

    on_clear_failed is called with the caught exception when the clipboard clear
    is attempted but fails (e.g. unsupported environment), allowing the caller
    to surface a notification without crashing.
    """
    global _auto_clear_timer
    if _auto_clear_timer is not None:
        _auto_clear_timer.cancel()
        _auto_clear_timer = None

    def _clear():
        global _auto_clear_timer
        _auto_clear_timer = None
        try:
            import pyperclip
            current = pyperclip.paste()
            if current == copied_text:
                pyperclip.copy("")
                if callback:
                    callback()
        except Exception as exc:
            if on_clear_failed:
                on_clear_failed(exc)

    _auto_clear_timer = threading.Timer(delay_seconds, _clear)
    _auto_clear_timer.daemon = True
    _auto_clear_timer.start()
    return _auto_clear_timer
