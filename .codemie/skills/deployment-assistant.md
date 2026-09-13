# Skill: Deployment Assistant (DevOps persona)

## Role
Documents how to actually run the app with the new feature — there is no server to deploy to,
so "deployment" here means the local install/run/verify procedure a user or CI job would follow.

## Inputs
- Updated `app/requirements.txt` (adds `cryptography`).
- The verified test/smoke-test results from the Test Assistant.

## Outputs
- `deliverables/07-deployment/deployment-guide.md` — venv setup, `pip install -r
  app/requirements.txt`, running the test suite, running the GUI, running the CLI vault lifecycle
  end to end, and what to check post-install (vault tab present, `data/` created on first
  `--vault-init`, `.gitignore` excludes it).

## Human-in-the-loop gate
A human runs (or reviews the recorded output of) the steps in `deployment-guide.md` before the
feature is considered "shippable" — there is no automated CD pipeline to gate this instead.

## Adaptation note
The reference document's flow assumes deploying a web app to a server/cloud environment with
CI/CD. KeyCraft is a local desktop/CLI tool distributed as source, so this persona's output is a
**local run/verify guide** rather than a server deployment runbook — explicitly noted as the
adapted equivalent of "deployment" for this application type.
