# Architecture — Encrypted Local Password Vault

**Persona:** Design Assistant (Architect) · **Status:** Approved

## Component diagram (text form)

```
                    ┌───────────────────────────┐
                    │        app/core/vault.py       │
                    │ ─────────────────────────  │
                    │  init_vault / unlock_vault  │
                    │  add_entry / list_entries    │
                    │  get_entry_password          │
                    │  delete_entry / vault_exists │
                    └─────┬───────────────┬───────┘
                          │               │
              reads/writes│               │executes DDL from
                          ▼               ▼
                 app/data/vault.db      app/db/schema.sql
                 (SQLite, gitignored)

        consumed by:
        ┌───────────────────────┐      ┌──────────────────────────────┐
        │ app/cli/cli_runner.py      │      │ app/gui/components/vault_panel.py │
        │ --vault-init/add/list/  │      │ VaultPanel (locked/unlocked   │
        │ show/delete flags       │      │ views), used from             │
        │ getpass.getpass() for   │      │ app/gui/app_window.py's           │
        │ master password         │      │ "🔐 Vault" tab                │
        └───────────────────────┘      └──────────────────────────────┘
```

`app/core/vault.py` is the only module that touches SQLite or the `cryptography` library. Neither the
CLI nor the GUI layer ever derives keys or runs SQL directly — they only call the public
functions above, mirroring how `app/core/generator.py` is the sole owner of `secrets`-based
randomness for the rest of the app.

## Encryption boundary

```
master password (never stored)
        │
        ▼  PBKDF2-HMAC-SHA256, 200,000 iterations, random 16-byte salt
   derived key (32 bytes, base64url-encoded for Fernet)
        │
        ▼  Fernet(derived_key)
   ┌─────────────────────────────┬──────────────────────────────┐
   │ encrypts a fixed verifier    │ encrypts/decrypts each entry's│
   │ string, stored once in       │ password on add/reveal        │
   │ vault_meta.verifier          │ (vault_entries.encrypted_password)│
   └─────────────────────────────┴──────────────────────────────┘
```

The derived key exists only in memory for the lifetime of a `VaultSession` (one unlock ≈ one
CLI invocation, or one GUI session until "🔒 Lock" is pressed). It is never persisted.

## Why SQLite + Fernet (vs. alternatives considered)
- **SQLite** (stdlib `sqlite3`): no new runtime dependency, matches KeyCraft's "no network, no
  external services" posture, trivially backed up as a single file.
- **Fernet** (`cryptography` library, one new dependency): authenticated encryption (AES-128-CBC
  + HMAC) with a simple, hard-to-misuse API — appropriate for a project of this size versus
  hand-rolling AES-GCM.
- **PBKDF2-HMAC-SHA256** over bcrypt/scrypt/argon2: available in the `cryptography` package
  already being added, no extra dependency, and iteration count is tunable; acceptable for a
  local single-user vault threat model (see `05-code-review/code-review-notes.md` for the
  explicit accepted risk).

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user), as part of the overall plan approval before implementation
began. **Decision:** Approved without changes.
