# Implementation Plan — KAN-33 (ENH-01) Auto-clear clipboard after copying generated password (GUI & CLI)

**Jira:** KAN-33 — ENH-01: Auto-clear clipboard after copying generated password (GUI & CLI)  
**Status:** Design proposed — **requires human approval before development**  
**Repo:** `ps-capstone-repository` (KeyCraft)

## 0. Scope and assumptions

### In scope (per KAN-33)
- Optional, configurable clipboard auto-clear timer after a successful copy.
- Works consistently across:
  - **GUI** copy workflows (generated password copy button).
  - **CLI** copy workflow **where clipboard copy already exists**.
- User feedback:
  - Confirm copy succeeded.
  - If enabled, indicate clipboard will clear after **N** seconds.
- Unit tests using mocks (no real clipboard dependency); avoid real sleeping.

### Out of scope
- OS-level secure clipboard APIs, multi-clipboard support.
- Persisting settings across sessions (unless an existing settings/persistence pattern exists).
- New automation infrastructure for native desktop GUI (Playwright cannot drive Tkinter).

### Constraints / security
- Do not log or print secrets in “cleared” messages.
- Reset/cancel prior pending timer when copying again.
- Only clear clipboard if it still contains the value the app last copied (avoid wiping user’s newer clipboard content).

## 1. Impacted components and files

### Core
- `app/core/clipboard.py`
  - Ensure a single active timer.
  - Schedule clear with guard (clipboard content matches copied value).
  - Provide optional callback hook for UI messaging.

### GUI
- `app/gui/components/password_display.py`
  - After successful copy, if auto-clear enabled schedule clear.
  - Display copy success confirmation (already present).
  - Add message that clipboard will clear in N seconds (if enabled) — either inline badge/text or reuse existing button-toast pattern.

- `app/gui/components/options_panel.py`
  - Add or confirm presence of toggle + delay seconds input.
  - Validate delay (non-positive → default 30 or treat as disabled per agreed behavior).

- `app/gui/app_window.py`
  - Wire options panel getters into password display via callback injection.

### CLI
- `app/cli/cli_runner.py`
  - Add flags:
    - `--auto-clear` (bool; only meaningful with `--copy`)
    - `--clear-delay SECONDS` (int; default 30)
  - After successful copy, schedule auto-clear when enabled.
  - Print non-secret feedback to stderr: “Clipboard will be cleared in N seconds.”

### Tests
- `app/tests/test_clipboard.py`
  - Timer scheduling unit tests (mock `threading.Timer`).
  - Guard behavior tests (mock `pyperclip.paste/copy`).

- (Optional) `e2e/tests/kan33-clipboard-autoclear.spec.js`
  - CLI behavior validation via subprocess (no GUI automation).

## 2. Work breakdown (frontend/backend)

> Note: KeyCraft is a local desktop app; tasks are grouped by **GUI/CLI/Core** rather than “frontend/backend”.

### 2.1 Core tasks
1. **Clipboard scheduler utility**
   - Confirm `schedule_auto_clear_clipboard(copied_text, delay_seconds, callback)` exists.
   - Ensure behavior:
     - Cancels previous timer.
     - Clears only when clipboard content equals `copied_text` at fire time.
     - Runs timer as daemon thread.
2. **Add cancel helper**
   - Ensure `cancel_auto_clear_clipboard()` exists for resets/tests.

### 2.2 GUI tasks
1. **Settings controls**
   - Toggle: enable/disable clipboard auto-clear.
   - Delay input: seconds.
   - Validation:
     - Parse int.
     - If <= 0 or invalid → fallback to 30 seconds.
2. **Wire settings into copy flow**
   - On copy success:
     - Show “Copied!” confirmation.
     - If enabled: schedule auto-clear with delay.
     - (If implemented) show informational message “Will clear in N seconds”.
3. **Regression checks**
   - Copy behavior unchanged when disabled.
   - Mask/unmask and regenerate unaffected.

### 2.3 CLI tasks
1. **Argparse flags**
   - Implement `--auto-clear` and `--clear-delay`.
   - Validation:
     - If `--clear-delay` <= 0 → coerce to default 30 (or treat as disabled if approved).
2. **Copy flow wiring**
   - When `--copy` is used:
     - Copy the first generated secret to clipboard.
     - If `--auto-clear`: schedule clear and emit message to stderr.

## 3. Database changes
- **None.** Clipboard feature does not require persistence.

## 4. Testing activities

### 4.1 Unit tests (Python)
- `app/tests/test_clipboard.py`
  - Default delay = 30.
  - Custom delay honored.
  - Repeated scheduling cancels previous timer.
  - Cancel function stops pending timer.
  - Clears clipboard only when value matches (mock paste returning copied text).
  - Does not clear when clipboard changed.

### 4.2 E2E / integration tests
- Because KeyCraft is Tkinter, **Playwright cannot automate GUI**.
- Add a Node-based Playwright test (subprocess) for **CLI flags** only, if desired.

### 4.3 Manual test checklist
- GUI:
  - Generate → Copy → observe confirmation → clipboard cleared after delay.
  - Copy twice within delay → only latest timer applies.
  - Disable auto-clear → clipboard remains.
  - Set delay to 1–2 seconds → quick clear.
- CLI:
  - `--copy` works.
  - `--copy --auto-clear --clear-delay 1` prints message and clears (environment permitting).

## 5. Build and deployment activities

### Build
- No packaging changes required.
- Ensure dependencies already present for clipboard operations (pyperclip optional).

### Deployment
- Local run only:
  - `pip install -r app/requirements.txt`
  - GUI: `python app/main.py`
  - CLI: `python app/main.py --help`

## 6. Rollout / backward compatibility
- Default behavior should remain unchanged when auto-clear is disabled.
- CLI flags are additive; no breaking changes to existing commands.

## 7. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Clipboard access may fail in headless or restricted environments | Catch exceptions; no crash; tests mock clipboard APIs |
| Clearing clipboard could wipe user’s new clipboard content | Guard check: only clear if clipboard still matches copied text |
| Multiple timers overlap causing unpredictable clearing | Single module-level active timer; cancel/reset on new copy |

---
## Human approval gate
**Approval required:** This plan + design artifacts must be approved before any development begins.
