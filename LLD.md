# Low-Level Design (LLD) — KAN-33 (ENH-01) Clipboard Auto-clear

**Jira:** KAN-33 — ENH-01: Auto-clear clipboard after copying generated password (GUI & CLI)  
**Status:** Design proposed — **requires human approval before development**

## 1. Impacted modules and contracts

### 1.1 `app/core/clipboard.py`

#### Public API (existing / to confirm)
```python
def copy_to_clipboard(text: str, root_window: Optional[tk.Tk] = None) -> bool:
    """Copy text to clipboard using pyperclip or Tk fallback."""

def schedule_auto_clear_clipboard(
    copied_text: str,
    delay_seconds: int = 30,
    callback: Optional[Callable[[], None]] = None,
) -> None:
    """Schedule clipboard clear after delay; cancel previous schedule; guard-match clipboard."""

def cancel_auto_clear_clipboard() -> None:
    """Cancel any pending auto-clear timer."""
```

#### Internal state
- Module-level:
  - `_active_timer: Optional[threading.Timer]`

#### Algorithm (schedule)
1. If `_active_timer` exists:
   - call `cancel()`
   - set `_active_timer = None`
2. Define `_clear()` closure:
   - set `_active_timer = None`
   - attempt `pyperclip.paste()`
   - if `current == copied_text`:
     - `pyperclip.copy("")`
     - if `callback`: call it
   - swallow all exceptions
3. Create `threading.Timer(float(delay_seconds), _clear)`
4. Set `timer.daemon = True`
5. Start timer and store it in `_active_timer`

#### Notes
- **Guard check** is mandatory.
- Timer must be daemon so application exit is not blocked.

### 1.2 GUI — `app/gui/components/options_panel.py`

#### Settings state
- `self.var_auto_clear: ctk.BooleanVar`
- `self.delay_entry: ctk.CTkEntry`

#### Getters
```python
def get_auto_clear_enabled(self) -> bool:
    return self.var_auto_clear.get()

def get_auto_clear_delay(self) -> int:
    # parse int; if invalid or <= 0 return 30
```

#### Validation
- `int(self.delay_entry.get())`
- On `ValueError/TypeError` → return `30`
- If parsed <= 0 → return `30`

### 1.3 GUI — `app/gui/components/password_display.py`

#### Copy flow
- On Copy click:
  1. call `copy_to_clipboard(self.current_password, root_window=self.winfo_toplevel())`
  2. show existing “✓ Copied!” button feedback
  3. determine settings:
     - default internal values
     - override from injected `get_clipboard_settings()` returning `(enabled: bool, delay: int)`
  4. if enabled:
     - call `schedule_auto_clear_clipboard(self.current_password, delay_seconds=delay)`

#### Optional UI message enhancement
If product wants explicit messaging beyond the copy button:
- Add a label (non-secret) under the action row, updated on copy:
  - `"Clipboard will clear in {delay}s"`
  - reset/clear label when auto-clear fires (use callback)

This is optional because the story allows a “status message” pattern and the button change may be sufficient.

### 1.4 GUI — `app/gui/app_window.py`
- Provide settings getter callback from `OptionsPanel` to `PasswordDisplay`:
```python
get_clipboard_settings=self._get_clipboard_settings

def _get_clipboard_settings(self) -> tuple:
    return (
        self.options_panel.get_auto_clear_enabled(),
        self.options_panel.get_auto_clear_delay(),
    )
```

### 1.5 CLI — `app/cli/cli_runner.py`

#### Argparse additions
```python
parser.add_argument("--copy", action="store_true", help="Copy the generated password to clipboard")
parser.add_argument("--auto-clear", action="store_true", help="Auto-clear clipboard after copying (requires --copy)")
parser.add_argument("--clear-delay", type=int, default=30, metavar="SECONDS", help="Seconds before auto-clearing clipboard (default: 30, requires --auto-clear)")
```

#### Copy wiring
```python
if parsed.copy and passwords:
    copy_to_clipboard(passwords[0])
    if parsed.auto_clear:
        delay = parsed.clear_delay if parsed.clear_delay > 0 else 30
        schedule_auto_clear_clipboard(passwords[0], delay_seconds=delay)
        print(f"Clipboard will be cleared in {delay} seconds.", file=sys.stderr)
```

## 2. Testing design

### 2.1 Unit tests — `app/tests/test_clipboard.py`
- Patch `core.clipboard.threading.Timer` to avoid real sleeping.
- Validate:
  - default delay argument = `30.0`
  - custom delay argument honored
  - repeated schedule cancels previous timer
  - cancel clears `_active_timer`
  - clear guard behavior using `@patch("pyperclip.paste")` and `@patch("pyperclip.copy")`

### 2.2 CLI integration (optional)
- Use Node/Playwright test harness that shells out to python, validating:
  - `--help` contains flags
  - `--copy --auto-clear --clear-delay 1` prints expected message

## 3. Backward compatibility
- If GUI toggle is off (or default-off per product choice), copy behavior remains as-is.
- CLI behavior unchanged unless user passes new flags.

---
## Human approval gate
**Approval required:** This LLD must be approved before implementation.

**Reviewed by:** _TBD_  
**Decision:** _TBD_  
**Date:** _TBD_
