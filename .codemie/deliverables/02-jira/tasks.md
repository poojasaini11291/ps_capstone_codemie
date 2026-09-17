# Engineering Tasks — Epic KC-100 (Encrypted Local Password Vault)

**Persona:** Requirement Assistant (BA), broken down for the Code Assistant · **Status:** All Done

## Under KC-101 / KC-102 (create & unlock)
- **KC-111** — Design & write `app/db/schema.sql` (`vault_meta`, `vault_entries`). → `app/db/schema.sql`
- **KC-112** — Implement `_derive_key` (PBKDF2-HMAC-SHA256, 200k iters) and the verifier
  scheme in `app/core/vault.py`. → `app/core/vault.py`
- **KC-113** — Implement `vault_exists`, `init_vault`, `unlock_vault` + exception hierarchy
  (`VaultError`, `VaultNotInitializedError`, `VaultAlreadyInitializedError`, `VaultAuthError`).
  → `app/core/vault.py`
- **KC-114** — Add `cryptography` to `app/requirements.txt`; add `.gitignore` excluding `data/`.

## Under KC-103 (save)
- **KC-115** — Implement `add_entry()` with label/password required, username optional.
  → `app/core/vault.py`
- **KC-116** — Add `--vault-init`, `--vault-add`, `--username` CLI flags with `getpass` prompts.
  → `app/cli/cli_runner.py`, `app/main.py`
- **KC-117** — Add "Save Current Password" row to the GUI vault panel.
  → `app/gui/components/vault_panel.py`

## Under KC-104 (list & reveal)
- **KC-118** — Implement `list_entries()` (metadata only) and `get_entry_password()` (decrypt
  on demand). → `app/core/vault.py`
- **KC-119** — Add `--vault-list`, `--vault-show` CLI flags. → `app/cli/cli_runner.py`
- **KC-120** — Add scrollable entry list with Reveal/Hide + Copy (reusing
  `core.clipboard.copy_to_clipboard`) to the GUI vault panel. → `app/gui/components/vault_panel.py`

## Under KC-105 (delete)
- **KC-121** — Implement `delete_entry()`. → `app/core/vault.py`
- **KC-122** — Add `--vault-delete` CLI flag. → `app/cli/cli_runner.py`
- **KC-123** — Add Delete button + confirmation dialog to each GUI entry row.
  → `app/gui/components/vault_panel.py`

## Cross-cutting
- **KC-124** — Wire the new "🔐 Vault" tab into `app/gui/app_window.py`.
- **KC-125** — Write `app/tests/test_vault.py` (9 cases, see `../06-testing/vault.feature`).
- **KC-126** — Update root `README.md` (features, CLI usage, architecture tree).
- **KC-127** — Run full test suite + manual CLI/GUI smoke test; record in
  `../06-testing/test-execution-report.md`.
