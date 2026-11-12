# Wireframes — KAN-33 (ENH-01) Clipboard Auto-clear (GUI & CLI)

**Jira:** KAN-33 — ENH-01: Auto-clear clipboard after copying generated password (GUI & CLI)  
**Status:** Design proposed — **requires human approval before development**

## 1. GUI wireframes

### 1.1 Generator tab — clipboard settings (OptionsPanel section)

```
┌───────────────────────────────────────────────┐
│ Clipboard Security                            │
│                                               │
│ [x] Auto-clear clipboard after copy           │
│                               Delay (s): [30] │
└───────────────────────────────────────────────┘

Rules:
- If unchecked: no timer scheduled.
- Delay input accepts integers; invalid/<=0 falls back to 30.
```

### 1.2 Password display — copy feedback

Current pattern (exists): button changes to “✓ Copied!” briefly.

Enhanced (recommended): show an additional non-secret status line under the buttons.

```
┌───────────────────────────────────────────────┐
│                Generated Password             │
│  [ ***************password*************** ]   │
│                                               │
│ [👁 Hide] [🔄 Regenerate]     [📋 Copy to Clipboard] │
│                                               │
│ Status: Copied. Clipboard will clear in 30s   │  ← only if auto-clear enabled
└───────────────────────────────────────────────┘

If auto-clear disabled:
- Status: Copied.

If clipboard clear fires (optional):
- Status: Clipboard cleared.
```

## 2. CLI UX examples

### 2.1 Help
```
$ python app/main.py --help
...
--copy
--auto-clear
--clear-delay SECONDS
...
```

### 2.2 Copy + auto-clear
```
$ python app/main.py -l 16 --copy --auto-clear --clear-delay 30
<password output>
(stderr) Clipboard will be cleared in 30 seconds.
```

---
## Human approval gate
**Approval required:** These wireframes must be approved before implementation.

**Reviewed by:** _TBD_  
**Decision:** _TBD_  
**Date:** _TBD_
