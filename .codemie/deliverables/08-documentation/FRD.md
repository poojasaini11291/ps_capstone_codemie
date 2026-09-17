# Functional Requirements Document — Encrypted Local Password Vault

**Persona:** Documentation Assistant (Technical Writer) · **Status:** Final
**Applies to:** KeyCraft, Epic KC-100

## 1. Purpose & scope
This FRD describes the functional and non-functional requirements of the encrypted local vault
feature added to KeyCraft, as actually implemented and tested (see traceability table below),
not as originally speculated.

## 2. Functional requirements

| ID | Requirement | Traces to (story) | Traces to (test) |
|---|---|---|---|
| FR-1 | The system shall allow creating exactly one vault per `app/data/vault.db`, protected by a master password of at least 8 characters. | KC-101 | `test_init_creates_vault`, `test_init_twice_raises` |
| FR-2 | The system shall allow unlocking an existing vault by re-entering the correct master password, and shall reject an incorrect one without granting access. | KC-102 | `test_unlock_with_correct_password_succeeds`, `test_unlock_with_wrong_password_raises` |
| FR-3 | The system shall allow saving a password under a required label and optional username while the vault is unlocked. | KC-103 | `test_add_list_get_delete_round_trip`, `test_add_entry_requires_label_and_password` |
| FR-4 | The system shall allow listing saved entries (label, username, timestamps) without decrypting any password. | KC-104 | `test_add_list_get_delete_round_trip` |
| FR-5 | The system shall allow decrypting and displaying a single specified entry's password on demand. | KC-104 | `test_add_list_get_delete_round_trip` |
| FR-6 | The system shall allow deleting a specified entry, succeeding silently (returning false, not raising) if the id does not exist. | KC-105 | `test_delete_nonexistent_entry_returns_false` |
| FR-7 | Every vault operation available in the GUI shall also be available as a CLI flag, and vice versa. | KC-101..105 | Manual CLI + GUI smoke tests, `../06-testing/test-execution-report.md` §3–4 |

## 3. Non-functional requirements

| ID | Requirement | Verified by |
|---|---|---|
| NFR-1 | The master password shall never be persisted in any form. | Code review (`../05-code-review/code-review-notes.md`); design inspection of `app/core/vault.py` |
| NFR-2 | The master password shall never be accepted as a CLI argument or otherwise appear in shell history or process listings. | Code review; `getpass.getpass()` used exclusively |
| NFR-3 | Every stored password shall be encrypted at rest. | `test_entries_are_encrypted_at_rest` |
| NFR-4 | The feature shall require no network access. | Design inspection — `app/core/vault.py` only touches local SQLite |
| NFR-5 | The vault database file shall be excluded from version control. | `.gitignore` inspection |

## 4. Out of scope (explicitly, per the epic)
Multi-user vaults, cloud sync/backup, password rotation reminders, browser autofill/integration,
importing credentials from other password managers.

## 5. User-facing documentation
End-user-facing usage (feature description, CLI examples) lives in the root `README.md`, under
"🔐 Encrypted Local Vault" and the extended "💻 CLI Usage" section — kept in sync with this FRD
but written for an end user rather than a requirements audience.

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user) — this FRD and the root `README.md` were checked against
the actually-running feature (tests passing, CLI lifecycle verified, GUI tab present and
functional) before being treated as final documentation.
