# Architecture — KAN-33 (ENH-01) Clipboard Auto-clear (GUI & CLI)

**Jira:** KAN-33 — ENH-01: Auto-clear clipboard after copying generated password (GUI & CLI)  
**Status:** Design proposed — **requires human approval before development**

## 1. Context
KeyCraft is a local-only Python application with:
- GUI (CustomTkinter) in `app/gui/*`
- CLI (argparse) in `app/cli/cli_runner.py`
- Core utilities in `app/core/*`

Clipboard operations are centralized in `app/core/clipboard.py` and used by both the GUI and CLI.

## 2. Target architecture change (what changes for KAN-33)
Add a *single, shared* auto-clear scheduling mechanism to the clipboard module and wire it into:
- GUI copy workflow (generated password copy button)
- CLI copy workflow (`--copy`)

Auto-clear is **optional** (enable/disable), with a configurable delay and safe behavior:
- Only one active timer.
- Cancel prior timer on new copy.
- Only clear if clipboard still contains the value last copied by KeyCraft.

## 3. Component diagram (text)

```
                 ┌───────────────────────────────┐
                 │        app/core/clipboard.py  │
                 │  - copy_to_clipboard(text)    │
                 │  - schedule_auto_clear_clipboard(
                 │       copied_text, delay, cb) │
                 │  - cancel_auto_clear_clipboard│
                 └───────────────┬───────────────┘
                                 │
                uses clipboard API│ (pyperclip, tkinter fallback)
                                 ▼
                           System Clipboard

  consumed by:

  ┌───────────────────────────────┐        ┌───────────────────────────────┐
  │  app/gui/components/password_  │        │        app/cli/cli_runner.py  │
  │  display.py                    │        │  --copy                       │
  │  - Copy button                 │        │  --auto-clear / --clear-delay │
  │  - Reads settings from options │        │  - calls schedule_auto_clear   │
  └───────────────┬───────────────┘        └───────────────────────────────┘
                  │
                  │ injected getter
                  ▼
  ┌───────────────────────────────┐
  │ app/gui/components/options_    │
  │ panel.py                       │
  │ - toggle enable/disable        │
  │ - delay seconds input          │
  └───────────────────────────────┘
```

## 4. Data flow / interaction summary

### GUI: Generate → Copy → Auto-clear
1. User clicks **Copy to Clipboard** in `PasswordDisplay`.
2. `copy_to_clipboard(password, root_window=...)` executes.
3. UI shows a non-secret confirmation (existing “✓ Copied!”).
4. `PasswordDisplay` reads settings from `OptionsPanel` (enabled + delay).
5. If enabled, `schedule_auto_clear_clipboard(password, delay_seconds=...)` schedules a timer.
6. When timer fires:
   - reads clipboard content
   - clears only if content still equals the password we copied

### CLI: Generate → --copy → --auto-clear
1. User runs CLI with `--copy`.
2. CLI generates first password as today.
3. `copy_to_clipboard(password)` executes.
4. If `--auto-clear` provided, schedule clear with delay and print: “Clipboard will be cleared in N seconds.” (stderr).

## 5. Key architectural decisions
- **Single owner of clipboard side-effects:** `app/core/clipboard.py`.
- **No persistence required:** settings are in-session only unless there’s an existing settings store.
- **Safe clearing guard:** clear only if clipboard still contains the value we copied.
- **Desktop automation limitation:** GUI E2E automation not performed with Playwright; unit tests + CLI subprocess tests cover behavior.

## 6. Non-functional considerations
- **Security:** prevent wiping unrelated clipboard content; do not print secrets.
- **Reliability:** handle clipboard access failures without crashing.
- **UX:** provide clear, non-secret feedback that auto-clear is enabled and will run after N seconds.

---
## Human approval gate
**Approval required:** This architecture must be approved before implementation.

**Reviewed by:** _TBD_  
**Decision:** _TBD_  
**Date:** _TBD_
