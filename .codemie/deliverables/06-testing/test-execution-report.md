# Test Execution Report — Encrypted Local Password Vault

**Persona:** Test Assistant (QA) · **Status:** Passed, approved

## 1. Automated unit tests

**Command:** `cd app && python -m unittest discover -s tests -v`

**Result:** `Ran 22 tests in 0.921s — OK` (0 failures, 0 errors)

```
test_batch_generation ... ok
test_custom_lengths ... ok
test_default_password_generation ... ok
test_digits_only ... ok
test_exclude_ambiguous_characters ... ok
test_passphrase_generation ... ok
test_pin_generation ... ok
test_common_weak_password_detection ... ok
test_crack_time_formatting ... ok
test_entropy_calculation ... ok
test_sequential_patterns ... ok
test_strong_password ... ok
test_add_entry_requires_label_and_password ... ok
test_add_list_get_delete_round_trip ... ok
test_delete_nonexistent_entry_returns_false ... ok
test_entries_are_encrypted_at_rest ... ok
test_init_creates_vault ... ok
test_init_twice_raises ... ok
test_unlock_with_correct_password_succeeds ... ok
test_unlock_with_wrong_password_raises ... ok
test_unlock_without_init_raises ... ok
test_vault_does_not_exist_initially ... ok
```

13 pre-existing (generator + strength checker) + **9 new vault tests**, all passing.

## 2. Gherkin scenario → `unittest` mapping

| `06-testing/vault.feature` scenario | `app/tests/test_vault.py` method |
|---|---|
| No vault exists initially | `test_vault_does_not_exist_initially` |
| Creating a new vault | `test_init_creates_vault` |
| Cannot initialize a vault twice | `test_init_twice_raises` |
| Cannot unlock a vault that was never created | `test_unlock_without_init_raises` |
| Unlocking with the correct master password succeeds | `test_unlock_with_correct_password_succeeds` |
| Unlocking with the wrong master password fails | `test_unlock_with_wrong_password_raises` |
| Full save / list / reveal / delete round trip | `test_add_list_get_delete_round_trip` |
| Deleting a nonexistent entry fails gracefully | `test_delete_nonexistent_entry_returns_false` |
| Saving requires both a label and a password | `test_add_entry_requires_label_and_password` |
| Passwords are encrypted at rest | `test_entries_are_encrypted_at_rest` |

## 3. Manual CLI smoke test (full vault lifecycle)

Since `getpass.getpass()` reads from the real console (and hangs on piped stdin under Git Bash on
Windows — a known environment quirk, not a product bug), the CLI lifecycle was exercised via a
scripted harness that monkeypatches `getpass.getpass` to feed canned master-password values, then
calls `run_cli()` directly for each step:

| Step | Command (conceptually) | Result |
|---|---|---|
| 1 | `--vault-init` | "Vault initialized." |
| 2 | `--vault-list` | "Vault is empty." |
| 3 | `--length 20 --vault-add "Demo"` | Password generated + "Saved to vault as entry [1]." |
| 4 | `--vault-list` | Shows `[1] Demo - saved <timestamp>` |
| 5 | `--vault-show 1` | Prints the correct decrypted password |
| 6 | `--vault-show 1` with wrong master password | "Error: Incorrect master password." |
| 7 | `--vault-delete 1` | "Deleted." |
| 8 | `--vault-list` | "Vault is empty." again |

All steps produced correct output; no crashes or unhandled exceptions.

## 4. Manual GUI smoke test

A headless instantiation of `KeyCraftApp` confirmed:
- 4 tabs present, including "🔐 Vault".
- Programmatically driving `VaultPanel._create_vault()` then `_save_current()` produced a real
  SQLite row, decryptable back to the original plaintext, with the entry count and content
  matching expectations.

## 5. Cleanup
All smoke-test artifacts (the test `app/data/vault.db`, temporary harness script, stray
`__pycache__` directories) were removed after verification — none are part of the committed
codebase, consistent with `.gitignore` excluding `data/`.

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user) — test results presented and accepted as part of the
overall implementation verification before documentation was finalized.
