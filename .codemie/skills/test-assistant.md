# Skill: Test Assistant (QA persona)

## Role
Writes and executes automated tests for the vault feature, and records the results in a form a
human can verify without re-running the suite themselves.

## Inputs
- `deliverables/04-design/low-level-design.md` (the behavior contract).
- `deliverables/02-jira/user-stories.md` acceptance criteria.
- Existing test conventions: `app/tests/test_generator.py` (`unittest.TestCase`, no mocking, direct
  calls against real objects).

## Outputs
- `app/tests/test_vault.py` — 9 `unittest.TestCase` methods covering init/unlock success and failure,
  full add/list/get/delete round-trip, deleting a nonexistent entry, missing-field validation,
  and a direct assertion that plaintext passwords never appear in the raw `.db` file bytes.
- `deliverables/06-testing/vault.feature` — the same scenarios expressed as Gherkin, mapped 1:1
  to the `unittest` methods so a non-engineer reviewer can read the acceptance criteria.
- `deliverables/06-testing/test-execution-report.md` — actual output of running
  `cd app && python -m unittest discover -s tests` plus the manual CLI/GUI smoke tests performed.

## Human-in-the-loop gate
Test results are reported, not self-approved — a human confirms the pass rate and smoke-test
coverage recorded in `test-execution-report.md` before deployment docs are finalized.

## Adaptation note
The reference document's example flow (web app) suggests Playwright/Selenium for UI tests and
JUnit/TestNG for unit tests. KeyCraft is a Python desktop app with no browser layer, so this
persona uses **`unittest`** (matching the project's existing convention) for all automated
coverage, plus a manual/scripted GUI smoke test (headless `CTk` instantiation) in place of a
Selenium/Playwright UI-automation pass — recorded explicitly as manual verification in
`test-execution-report.md`, not disguised as automated E2E coverage.
