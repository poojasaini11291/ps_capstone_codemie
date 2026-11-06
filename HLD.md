# High-Level Design (HLD) — KAN-33 (ENH-01) Clipboard Auto-clear

**Jira:** KAN-33 — ENH-01: Auto-clear clipboard after copying generated password (GUI & CLI)  
**Status:** Design proposed — **requires human approval before development**

## 1. Overview
Implement an **optional** clipboard auto-clear feature that, after copying a generated secret to the system clipboard, clears it after a configurable delay.

The feature must behave consistently across GUI and CLI **where clipboard copy is supported**.

## 2. User experience

### 2.1 GUI
- Existing: user clicks **📋 Copy to Clipboard** and sees **✓ Copied!**.
- Enhanced:
  - If auto-clear enabled: schedule clipboard clear after **delay seconds**.
  - Provide user feedback that auto-clear is enabled and will clear after **N seconds**.

Configuration controls (in-session):
- Checkbox/toggle: **Auto-clear clipboard after copy**
- Delay input: **Delay (s)**

### 2.2 CLI
- Existing: user can run `--copy` to copy generated output to clipboard.
- Enhanced:
  - Add `--auto-clear` and `--clear-delay SECONDS`.
  - When auto-clear enabled, print to **stderr**:
    - `Clipboard will be cleared in N seconds.`

## 3. Functional behavior

### 3.1 Timer/reset semantics
- Only **one** auto-clear timer may be active.
- If the user copies again before the timer fires:
  - cancel the previous timer
  - start a new timer based on the latest copy

### 3.2 Safe-clear guard
At timer fire time:
- read current clipboard
- clear clipboard **only if** the clipboard still equals the value KeyCraft copied

This prevents KeyCraft from wiping unrelated clipboard content if the user copied something else after.

### 3.3 Default values
- Default delay: **30 seconds**.
- Invalid or non-positive delays:
  - Coerce to 30 seconds (preferred for backward compatibility and simplicity)
  - (Alternative if product prefers) treat as disabled; requires approval

## 4. Error handling
- Clipboard read/write can fail (missing clipboard provider, permissions, headless environment).
- All clipboard operations must fail **silently and safely**:
  - no crash
  - no stack trace in UI

## 5. Security and compliance
- Never display or log the secret in any auto-clear messages.
- Ensure clearing does not remove other user clipboard content (guard check).

## 6. Test strategy (high level)
- Unit test the scheduler using mocks for:
  - `threading.Timer`
  - `pyperclip.copy` / `pyperclip.paste`
- CLI behavior validated via subprocess test (optional), not GUI automation.

---
## Human approval gate
**Approval required:** This HLD must be approved before implementation.

**Reviewed by:** _TBD_  
**Decision:** _TBD_  
**Date:** _TBD_
