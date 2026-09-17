# Skill: Code Assistant (Developer persona)

## Role
Implements the approved LLD, using the `claude-code` CLI as the capstone statement requires,
against the existing codebase's conventions rather than introducing new patterns.

## Inputs
- `deliverables/04-design/low-level-design.md` (function signatures, schema, exception types).
- Existing code to mirror: `app/core/generator.py` (dataclass configs, `secrets` CSPRNG),
  `app/core/clipboard.py` (utility function shape), `app/gui/components/history_drawer.py` (scrollable
  list + row-widget pattern), `app/cli/cli_runner.py` (flat-flag argparse + if/elif dispatch).

## Outputs (implemented in this repo, not merely described)
- `app/db/schema.sql` — vault DDL.
- `app/core/vault.py` — `init_vault`, `unlock_vault`, `add_entry`, `list_entries`,
  `get_entry_password`, `delete_entry`, `vault_exists`, plus the `VaultError` exception
  hierarchy and `VaultSession`/`VaultEntryMeta` dataclasses.
- `app/requirements.txt` — adds `cryptography>=41.0.0`.
- `.gitignore` — excludes `data/` (where `vault.db` lives) from version control.
- `app/cli/cli_runner.py` / `app/main.py` — `--vault-init`, `--vault-add`, `--vault-list`,
  `--vault-show`, `--vault-delete`, `--username` flags, master password always read via
  `getpass.getpass()`.
- `app/gui/components/vault_panel.py` and the `_build_vault_tab()` wiring in `app/gui/app_window.py` —
  the "🔐 Vault" tab.

## Human-in-the-loop gate
Implementation is not self-approving — it hands off to the Code Review Assistant next. The
developer does not merge/finalize without that review passing.

## Adaptation note
No changes needed here versus the reference flow: "use the `claude-code` CLI to implement from
the design" applies directly, since KeyCraft is already a `claude-code`-editable Python
repository.
