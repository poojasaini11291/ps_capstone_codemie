# Gap Analysis & Enhancement Selection — KeyCraft

**Persona:** Requirement Assistant (BA) · **Status:** Approved (see `02-jira/epic.md`)

## 1. Current state of KeyCraft

KeyCraft (root `README.md`) is a Python/CustomTkinter desktop app + argparse CLI that:
- generates passwords, passphrases, and PINs via `secrets`-based CSPRNG (`app/core/generator.py`);
- scores password strength via Shannon entropy + pattern checks (`app/core/strength_checker.py`);
- copies to clipboard with auto-clear (`app/core/clipboard.py`);
- keeps an in-memory session history and batch export (`app/gui/components/history_drawer.py`).

Every one of these features is **stateless across runs** — nothing generated is ever saved. The
app has no persistence layer at all (no DB, no file storage of user data).

## 2. Gaps identified

| Gap | Impact | Evidence |
|---|---|---|
| No way to save a generated password for later use | A user who generates a strong password for, say, a new bank login has no way to retrieve it later from within the app — defeats the point of a password *manager*-adjacent tool | No `app/db/`, no `app/core/*.py` module touches disk beyond reading `app/core/wordlist.py` |
| No persistence layer exists at all | Any future stateful feature (saved passwords, saved presets, audit log) needs this foundational layer built first | Confirmed via full read of `app/core/`, `app/gui/`, `app/cli/` — zero `sqlite3`/file-write usage |
| No secrets-at-rest story | If persistence were added naively, it would risk storing secrets in plaintext | N/A — preventative, informs the design |

## 3. Enhancement selected: Encrypted Local Password Vault

Of the options considered (offline breach-check against a local hash list, saved config
profiles, encrypted local vault), the **encrypted local vault** was selected because it:
- closes the single biggest functional gap (no persistence) rather than a cosmetic one;
- introduces genuine new architectural surface — a DB schema, an encryption boundary, new CLI
  flags, and a new GUI tab — enough to meaningfully exercise every downstream SDLC persona
  (Design, Code Review, QA, Deployment, Docs) rather than a trivial one-file change;
- has a natural, auditable security story (PBKDF2 + Fernet, verifier-not-password storage) that
  gives the Code Review Assistant real material to review.

## 4. Non-functional constraints carried into design
- **Local-only**: no network calls, no cloud sync (matches KeyCraft's existing privacy posture).
- **No plaintext secrets at rest or in transit within the process** beyond the minimum needed to
  display them to the authenticated user on demand.
- **CLI/GUI parity**: every vault operation available in the GUI must also be available as a CLI
  flag, matching KeyCraft's existing dual-interface convention.
- **Master password never becomes a CLI argument** (shell history / process list exposure risk) —
  always collected interactively via `getpass`.
