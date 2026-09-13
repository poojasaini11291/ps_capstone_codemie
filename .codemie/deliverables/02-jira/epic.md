# EPIC: KC-100 — Encrypted Local Password Vault

**Project:** KeyCraft (KC) · **Type:** Epic · **Persona:** Requirement Assistant (BA)
**Status:** Done · **Priority:** High

## Summary
Add a master-password-protected, locally-encrypted vault so users can save, label, retrieve,
and delete generated passwords, from both the GUI and the CLI, without any of it ever leaving
the local machine or touching disk in plaintext.

## Description
KeyCraft currently generates and analyzes passwords but never persists them (see
`../01-analysis/gaps-and-enhancements.md`). This epic adds a SQLite-backed, Fernet-encrypted
vault, unlocked by a single master password whose derived key (via PBKDF2-HMAC-SHA256) is used
to encrypt/decrypt entries on the fly. The master password itself is never stored.

## Business value
Turns KeyCraft from a one-shot generator into a tool users can rely on across sessions, without
adopting the trust/complexity overhead of a cloud-synced password manager.

## Scope
**In scope:** vault init/unlock, add/list/reveal/delete entries, GUI tab, CLI flags, tests, docs.
**Out of scope:** multi-user vaults, cloud sync, password rotation reminders, browser
autofill/integration, importing from other password managers.

## Linked artifacts
- Stories: `user-stories.md` (KC-101..KC-105)
- Tasks: `tasks.md`
- Design: `../04-design/architecture.md`, `high-level-design.md`, `low-level-design.md`
- Tests: `../06-testing/vault.feature`
- Code: `app/core/vault.py`, `app/db/schema.sql`, `app/cli/cli_runner.py`, `app/gui/components/vault_panel.py`

## Acceptance criteria (epic-level)
- A user can create a vault with a master password (min. 8 characters) exactly once per
  installation; a second `--vault-init` on an existing vault fails safely.
- A user can unlock the vault with the correct master password and is rejected with a clear
  error on an incorrect one — without leaking *why* beyond "incorrect master password."
- A user can save the currently generated/checked password under a label (+ optional username),
  list saved entries by label without decrypting them, reveal/copy/delete a specific entry.
- Every one of the above is available identically from the CLI and the GUI.

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user) · **Decision:** Approved, via explicit selection of
"Encrypted local password vault" over the offline-breach-check and config-profile alternatives,
and approval of the full implementation plan before coding began.
