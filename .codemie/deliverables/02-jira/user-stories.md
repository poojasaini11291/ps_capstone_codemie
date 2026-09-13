# User Stories — Epic KC-100 (Encrypted Local Password Vault)

**Persona:** Requirement Assistant (BA) · **Status:** All Done

---

### KC-101 — Create a vault
**As a** first-time KeyCraft user
**I want** to set a master password and create a vault
**so that** I have a place to securely save passwords I generate.

- **Priority:** High · **Estimate:** 3 pts
- **Acceptance criteria:**
  - Given no vault exists, when I run `--vault-init` (CLI) or open the Vault tab (GUI) and enter
    a master password (≥8 chars) twice matching, a vault is created at `app/data/vault.db`.
  - Given a vault already exists, creating another one fails with a clear error instead of
    silently overwriting it.
  - The master password itself is never written to disk in any form.

### KC-102 — Unlock a vault
**As a** returning KeyCraft user
**I want** to unlock my existing vault with my master password
**so that** I can access my saved entries.

- **Priority:** High · **Estimate:** 2 pts
- **Acceptance criteria:**
  - Given a vault exists, entering the correct master password grants access to the entry list.
  - Given a vault exists, entering an incorrect master password is rejected with an "incorrect
    master password" error and no access is granted.

### KC-103 — Save a password to the vault
**As a** KeyCraft user who just generated a strong password
**I want** to save it under a label (and optional username)
**so that** I can retrieve it later instead of regenerating or forgetting it.

- **Priority:** High · **Estimate:** 3 pts
- **Acceptance criteria:**
  - Given an unlocked vault and a currently generated/checked password, saving with a label
    persists an encrypted entry and it appears in the entry list.
  - Saving without a label is rejected client-side with a validation message.
  - The `--vault-add LABEL [--username X]` CLI flag performs the same save on the password just
    generated/checked in that invocation.

### KC-104 — List and reveal saved entries
**As a** KeyCraft user with saved entries
**I want** to see my saved labels and reveal/copy a specific password on demand
**so that** I can use a saved credential without it being visible until I choose to reveal it.

- **Priority:** Medium · **Estimate:** 3 pts
- **Acceptance criteria:**
  - Listing entries shows label, optional username, and save date — never the password itself.
  - Revealing a specific entry (by id in CLI, by clicking "Reveal" in GUI) decrypts and shows
    only that entry's password.
  - Copying a revealed entry uses the same clipboard mechanism as generated passwords.

### KC-105 — Delete a saved entry
**As a** KeyCraft user
**I want** to delete a saved entry I no longer need
**so that** my vault doesn't accumulate stale credentials.

- **Priority:** Medium · **Estimate:** 1 pt
- **Acceptance criteria:**
  - Deleting a valid entry id removes it; it no longer appears in subsequent listings.
  - Deleting a nonexistent entry id fails gracefully (no crash, clear message), returns falsy.
  - GUI delete requires an explicit confirmation dialog before removing.

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user) · **Decision:** Approved as part of the overall
implementation plan approval (see `epic.md`).
