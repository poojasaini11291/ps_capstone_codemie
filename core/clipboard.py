import threading
import tkinter as tk
from typing import Optional, Callable


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
    root_window: Optional[tk.Tk] = None
):
    """
    Clears the clipboard after delay_seconds if it still contains the copied text.
    """
    def _worker():
        import time
        time.sleep(delay_seconds)
        try:
            import pyperclip
            current = pyperclip.paste()
            if current == copied_text:
                pyperclip.copy("")
                if callback:
                    callback()
        except Exception:
            pass

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

