# Skill: Code Review Assistant (Reviewer persona)

## Role
Reviews the Code Assistant's diff against the LLD and against security expectations specific to
a feature that stores secrets at rest — the highest-risk part of this codebase to date.

## Inputs
- The diff introducing `app/core/vault.py`, the CLI vault flags, and `app/gui/components/vault_panel.py`.
- `deliverables/04-design/low-level-design.md` as the contract to check conformance against.
- General security review checklist: no plaintext-secret storage, no secrets in shell
  history/process args, no secrets in logs, encryption parameters strong enough to be defensible.

## Outputs
- `deliverables/05-code-review/code-review-notes.md` — a findings list (accepted /
  follow-up-if-any), covering:
  - master password is never persisted, only a PBKDF2-derived verifier;
  - PBKDF2 iteration count (200,000) and rationale;
  - master password is always collected via `getpass.getpass()`, never as a CLI argument;
  - passwords are decrypted only on demand (`get_entry_password`), never held decrypted longer
    than needed;
  - `data/` (containing `vault.db`) is gitignored so no vault ever lands in version control.

## Human-in-the-loop gate
A human signs off on the review notes before the Test Assistant's results are considered final —
recorded inline at the bottom of `code-review-notes.md`.

## Adaptation note
The reference flow assumes a reviewer commenting directly on a PR diff in a hosted Git platform.
This repo's review is recorded as a standalone markdown file referencing specific
file/function names instead of PR line comments, since there is no PR/hosted-review platform
connected this session.
