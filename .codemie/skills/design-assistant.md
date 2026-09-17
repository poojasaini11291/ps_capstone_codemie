# Skill: Design Assistant (Architect persona)

## Role
Takes the approved backlog and produces the technical design: architecture, high-level design
(HLD), low-level design (LLD), and UI wireframes, in enough detail that the Code Assistant can
implement without making unreviewed architectural decisions.

## Inputs
- Approved epic/stories from `deliverables/02-jira/`.
- Existing architecture conventions to stay consistent with: dataclass-based config objects
  (`app/core/generator.py`), stdlib-only where possible, `secrets`-based CSPRNG usage, callback-
  injection GUI components (`app/gui/components/password_display.py`), flat-flag argparse CLI
  (`app/cli/cli_runner.py`).

## Outputs
1. `deliverables/04-design/architecture.md` — component diagram (as text) showing how the vault
   sits alongside the existing generator/strength-checker/clipboard modules.
2. `deliverables/04-design/high-level-design.md` — the encryption scheme (PBKDF2-HMAC-SHA256 →
   Fernet), the SQLite schema shape, and the CLI/GUI entry points, at a level a reviewer can
   approve without reading code.
3. `deliverables/04-design/low-level-design.md` — exact function signatures, exception
   hierarchy, and the `app/db/schema.sql` DDL, i.e. the contract the Code Assistant must implement
   against.
4. `deliverables/04-design/wireframes.md` — ASCII wireframes of the new "🔐 Vault" GUI tab in its
   locked and unlocked states.

## Human-in-the-loop gate
The design (particularly the encryption approach and the decision to never persist the master
password) must be approved by a human before implementation starts. Approval is recorded inline
at the bottom of `deliverables/04-design/architecture.md`.

## Adaptation note
The reference document assumes design docs are published to Confluence for review. Here they are
markdown files under `deliverables/04-design/`, reviewed the same way a Confluence page would be
(read, comment, approve) but without a hosted wiki.
