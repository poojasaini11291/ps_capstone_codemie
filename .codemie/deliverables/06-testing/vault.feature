Feature: Encrypted Local Password Vault
  As a KeyCraft user
  I want to save, list, reveal, and delete passwords in an encrypted local vault
  So that I can securely retrieve credentials I've generated, across sessions

  # Maps 1:1 to app/tests/test_vault.py — see mapping table in test-execution-report.md

  Scenario: No vault exists initially
    Given no vault database has been created
    Then the vault should report as not existing

  Scenario: Creating a new vault
    Given no vault exists
    When I initialize a vault with master password "correct-horse-battery"
    Then the vault should report as existing

  Scenario: Cannot initialize a vault twice
    Given a vault already exists
    When I try to initialize another vault at the same location
    Then it should fail with "vault already initialized"

  Scenario: Cannot unlock a vault that was never created
    Given no vault exists
    When I try to unlock it with any password
    Then it should fail with "vault not initialized"

  Scenario: Unlocking with the correct master password succeeds
    Given a vault initialized with master password "correct-horse-battery"
    When I unlock it with "correct-horse-battery"
    Then I should receive a valid vault session

  Scenario: Unlocking with the wrong master password fails
    Given a vault initialized with master password "correct-horse-battery"
    When I unlock it with "wrong-password"
    Then it should fail with "incorrect master password"

  Scenario: Full save / list / reveal / delete round trip
    Given an unlocked vault
    When I save the password "S3cur3P@ss!" under label "Gmail" with username "alice@example.com"
    Then listing entries should show exactly one entry labeled "Gmail" for "alice@example.com"
    And revealing that entry should return "S3cur3P@ss!"
    When I delete that entry
    Then listing entries should show no entries

  Scenario: Deleting a nonexistent entry fails gracefully
    Given an unlocked vault with no entries
    When I try to delete entry id 999
    Then the delete should report that nothing was removed, without raising an error

  Scenario: Saving requires both a label and a password
    Given an unlocked vault
    When I try to save an entry with an empty label
    Then it should be rejected as invalid
    When I try to save an entry with an empty password
    Then it should be rejected as invalid

  Scenario: Passwords are encrypted at rest
    Given an unlocked vault
    When I save the password "PlaintextSecret123" under label "Bank"
    Then the raw vault database file on disk should not contain "PlaintextSecret123" anywhere
