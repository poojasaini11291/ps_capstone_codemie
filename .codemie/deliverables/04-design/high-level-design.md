# High-Level Design — Encrypted Local Password Vault

**Persona:** Design Assistant (Architect) · **Status:** Approved

## 1. Data model (conceptual)

- **Vault** — exactly one per `vault.db` file. Holds the salt used for key derivation and a
  verifier token used to check a candidate master password without ever storing the password.
- **Entry** — belongs to the vault. Has a label (required), an optional username, an encrypted
  password, and created/updated timestamps.

## 2. Lifecycle

1. **Init** — user picks a master password (≥8 chars). A random salt is generated. A key is
   derived and used to encrypt a known constant ("verifier"). Salt + verifier are stored;
   `vault_entries` table is created empty.
2. **Unlock** — user re-enters the master password. The stored salt re-derives the same key
   *if and only if* the password matches. Decrypting the stored verifier and comparing it to the
   known constant proves correctness without ever comparing passwords directly.
3. **Use** — while unlocked (a `VaultSession` held in memory), the user can add/list/reveal/
   delete entries. Listing never decrypts; revealing decrypts exactly one entry on demand.
4. **Lock** — the in-memory session (and its derived key) is discarded. GUI: pressing "🔒 Lock".
   CLI: implicit — each CLI invocation unlocks fresh and discards the session on exit.

## 3. Interfaces

### CLI (`app/cli/cli_runner.py`)
| Flag | Effect |
|---|---|
| `--vault-init` | Create a new vault (prompts master password twice) |
| `--vault-add LABEL [--username U]` | Save the password generated/checked in this same invocation |
| `--vault-list` | Print id/label/username/created_at for every entry (no passwords) |
| `--vault-show ID` | Decrypt and print one entry's password |
| `--vault-delete ID` | Delete one entry |

All five prompt for the master password via `getpass.getpass()`; it is never a flag value.

### GUI (`app/gui/components/vault_panel.py`, "🔐 Vault" tab)
- **Locked view**: "Create Your Vault" (new) or "Unlock Your Vault" (existing), single or
  double password field, inline validation errors.
- **Unlocked view**: header with Lock button; save-current-password row (label + username +
  Save); scrollable list of entries, each with Reveal/Hide, Copy, Delete (with confirm dialog).

## 4. Non-functional requirements
- No entry password is ever logged, printed outside an explicit `--vault-show`/"Reveal" action,
  or written anywhere except as a Fernet ciphertext in `vault_entries.encrypted_password`.
- `app/data/vault.db` is excluded from version control via `.gitignore`.
- All vault errors surface as subclasses of `VaultError`, letting both the CLI and GUI catch one
  base type and display a user-facing message without leaking internals (e.g. stack traces).

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user). **Decision:** Approved as part of the overall plan.
