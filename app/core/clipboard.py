import threading
import tkinter as tk
from typing import Optional, Callable

_active_timer: Optional[threading.Timer] = None


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
    delay_seconds: int = 30,
    callback: Optional[Callable[[], None]] = None,
) -> None:
    """
    Clears the clipboard after delay_seconds if it still contains copied_text.
    Cancels any previously scheduled auto-clear so repeated copies reset the timer.
    Only clears if the clipboard still matches the copied value at fire time.
    """
    global _active_timer

    if _active_timer is not None:
        _active_timer.cancel()
        _active_timer = None

    def _clear() -> None:
        global _active_timer
        _active_timer = None
        try:
            import pyperclip
            # Only clear if clipboard still holds the password we copied
            current = pyperclip.paste()
            if current == copied_text:
                pyperclip.copy("")
                if callback:
                    callback()
        except Exception:
            pass

    timer = threading.Timer(float(delay_seconds), _clear)
    timer.daemon = True
    timer.start()
    _active_timer = timer


def cancel_auto_clear_clipboard() -> None:
    """Cancel any pending auto-clear timer."""
    global _active_timer
    if _active_timer is not None:
        _active_timer.cancel()
        _active_timer = None
