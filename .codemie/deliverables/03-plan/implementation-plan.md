# Implementation Plan — Epic KC-100 (Encrypted Local Password Vault)

**Persona:** Requirement Assistant (BA) / PM · **Status:** Executed as written

## Sequencing

```
1. Analysis & backlog (BA)        →  01-analysis/, 02-jira/                [HITL gate #1]
2. Design (Architect)             →  04-design/                            [HITL gate #2]
3. Implementation (Developer)     →  app/db/, app/core/vault.py, app/cli/, app/gui/
4. Code review (Reviewer)         →  05-code-review/                       [HITL gate #3]
5. Testing (QA)                   →  app/tests/test_vault.py, 06-testing/       [HITL gate #4]
6. Deployment docs (DevOps)       →  07-deployment/
7. Documentation (Tech Writer)    →  08-documentation/, README.md          [HITL gate #5]
```

Stages 1–2 are strictly sequential (design cannot start before backlog is approved). Stages
3 (DB layer → CLI → GUI, in that order, since CLI/GUI both depend on `app/core/vault.py`) happen
within a single implementation pass. Stages 4–5 both consume the same diff and can be thought of
as running in parallel conceptually, though in this session they were performed sequentially by
the same session for consistency. Stage 6–7 depend on 4–5 having passed.

## Human-in-the-loop (HITL) gates
1. **Backlog approval** — user selected the vault enhancement over two alternatives, and
   approved the deliverables-format decision (local markdown vs. live Jira/Confluence).
2. **Plan/design approval** — user approved the full implementation plan (this document's
   predecessor draft) via the plan-mode approval flow before any code was written.
3. **Code review approval** — recorded in `../05-code-review/code-review-notes.md`.
4. **Test results approval** — recorded in `../06-testing/test-execution-report.md`.
5. **Documentation accuracy check** — recorded in `../08-documentation/FRD.md`.

## Dependencies
- `app/core/vault.py` has no dependency on `app/gui/` or `app/cli/` — built and unit-tested first.
- `app/cli/cli_runner.py` and `app/gui/components/vault_panel.py` both depend only on `app/core/vault.py`'s
  public API, not on each other — either could be built first; CLI was built first here since it
  has a faster smoke-test loop (no windowing system required).
- `app/tests/test_vault.py` depends only on `app/core/vault.py`.
- Deployment/documentation depend on the feature being implemented *and* tested, per the "docs
  describe what was built, not what was planned" rule from the Documentation Assistant skill.

## Risk register
| Risk | Mitigation |
|---|---|
| Master password leaks via shell history or process list | Always collected via `getpass.getpass()`, never accepted as a CLI argument |
| Weak key derivation makes offline brute-force cheap | PBKDF2-HMAC-SHA256 with 200,000 iterations (see `04-design/high-level-design.md`) |
| Vault DB accidentally committed to git | `.gitignore` excludes `data/` (matches `app/data/` at any depth) from day one of the DB layer's existence |
| `getpass` hangs under piped/non-console stdin (observed during smoke testing on Windows/Git Bash) | Documented as a known environment quirk in `07-deployment/deployment-guide.md`; not a product bug, since real usage is via an interactive console or the GUI |
