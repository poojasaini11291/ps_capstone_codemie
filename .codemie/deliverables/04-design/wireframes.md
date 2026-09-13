# Wireframes — "🔐 Vault" GUI Tab

**Persona:** Design Assistant (Architect) · **Status:** Approved — matches the implemented
`app/gui/components/vault_panel.py`.

## Locked view — new vault

```
┌───────────────────────────────────────────────┐
│                                                 │
│              🔐 Create Your Vault              │
│  Set a master password to start saving         │
│  generated passwords locally, encrypted.        │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ Master password                    ●●●●●●● │ │
│  └───────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────┐ │
│  │ Confirm master password             ●●●●●● │ │
│  └───────────────────────────────────────────┘ │
│  [ error message if validation fails ]          │
│  ┌───────────────────────────────────────────┐ │
│  │              Create Vault                  │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
└───────────────────────────────────────────────┘
```

## Locked view — existing vault

Same card, title "🔐 Unlock Your Vault", single password field, button "Unlock".

## Unlocked view

```
┌───────────────────────────────────────────────────────────┐
│ 🔐 Saved Passwords                              [🔒 Lock] │
├───────────────────────────────────────────────────────────┤
│ [ Label______ ] [ Username (optional)______ ] [💾 Save Current Password] │
│ [ status message: "Saved 'Gmail' to the vault." ]           │
├───────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Gmail · alice@example.com      [👁 Reveal][📋 Copy][🗑]│   │
│ │ ••••••••                                              │   │
│ ├─────────────────────────────────────────────────────┤   │
│ │ Bank                            [👁 Reveal][📋 Copy][🗑]│   │
│ │ ••••••••                                              │   │
│ └─────────────────────────────────────────────────────┘   │
│                (scrollable list, empty-state message       │
│                 "No saved passwords yet." when empty)      │
└───────────────────────────────────────────────────────────┘
```

Clicking "👁 Reveal" swaps the masked label for the plaintext password in place and the button
becomes "🙈 Hide" (toggle, no separate modal). Clicking "🗑" opens a native confirm dialog
("Delete 'Gmail' from the vault?") before removing the row.

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user), as part of the overall plan approval.
