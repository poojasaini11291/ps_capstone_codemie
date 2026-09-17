# Code Review Notes — Encrypted Local Password Vault

**Persona:** Code Review Assistant · **Status:** Approved (no blocking findings)
**Reviewed diff:** `app/db/schema.sql`, `app/core/vault.py`, `app/requirements.txt`, `.gitignore`,
`app/cli/cli_runner.py`, `app/main.py`, `app/gui/components/vault_panel.py`, `app/gui/app_window.py`,
`app/tests/test_vault.py`.

## Security checklist

| Check | Result | Evidence |
|---|---|---|
| Master password never persisted | ✅ Pass | Only a PBKDF2-derived-key verifier is stored (`vault_meta.verifier`); the password itself only ever exists as a local variable, never assigned to any DB/file write |
| Master password never accepted as a CLI argument | ✅ Pass | All five `--vault-*` CLI paths in `cli_runner.py` call `getpass.getpass(...)`; no `argparse` flag accepts the password as a value |
| Passwords encrypted at rest | ✅ Pass | Confirmed by `app/tests/test_vault.py::test_entries_are_encrypted_at_rest` — raw `.db` bytes do not contain the plaintext password |
| Key derivation strength | ✅ Accepted | PBKDF2-HMAC-SHA256, 200,000 iterations, 16-byte random salt per vault — see risk note below |
| Decrypted secrets held in memory no longer than necessary | ✅ Pass | `get_entry_password` decrypts on each call; nothing decrypted is cached beyond the GUI's own `revealed_password` toggle state, which is cleared on "Hide" |
| Vault DB excluded from version control | ✅ Pass | `.gitignore` added covering `data/` (matches `app/data/`) before any vault code was written |
| Errors don't leak internals | ✅ Pass | All public functions raise `VaultError` subclasses with user-safe messages; CLI/GUI catch the base type uniformly |
| Input validation | ✅ Pass | `add_entry` raises `ValueError` on empty label/password; GUI additionally validates master-password length (≥8) and confirm-match before calling `init_vault` |

## Accepted risk: PBKDF2 vs. memory-hard KDFs
PBKDF2-HMAC-SHA256 is not memory-hard, unlike bcrypt/scrypt/argon2, so it is more amenable to
GPU-accelerated brute-force than those alternatives at equivalent wall-clock cost. **Accepted**
for this local, single-user, non-networked vault, because:
- it avoids adding a second new dependency beyond `cryptography` (which is already required for
  Fernet);
- the threat model is an attacker with local filesystem access to `app/data/vault.db`, who would
  also need to brute-force the master password itself — 200,000 iterations meaningfully raises
  the cost of that without changing the dependency footprint.
- Documented here explicitly rather than silently accepted, so a future maintainer can revisit
  it if the threat model changes (e.g. if vault files start being shared/synced).

## Style/consistency notes (non-blocking)
- `app/core/vault.py` mirrors the existing `@dataclass`-config convention from `app/core/generator.py`
  and the module-owns-its-side-effects pattern from `app/core/clipboard.py` — no deviation.
- `app/cli/cli_runner.py`'s new vault block follows the existing flat if/elif dispatch rather than
  introducing subcommands, consistent with the rest of the file.
- `app/gui/components/vault_panel.py` reuses `core.clipboard.copy_to_clipboard` rather than
  reimplementing clipboard logic — consistent with `password_display.py`.

## Verdict
**Approved.** No changes requested before merging into the test/deployment stages.

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user), as part of the overall verification pass (test suite +
manual smoke tests) confirming the implementation matches this review's expectations.
