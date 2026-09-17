# Skill: Documentation Assistant (Technical Writer persona)

## Role
Produces the end-user-facing and functional documentation for the finished feature, ensuring the
root `README.md` and a formal Functional Requirements Document (FRD) both describe what was
actually built (not what was planned) — written last, after implementation and testing are done.

## Inputs
- The merged, tested vault feature (`app/core/vault.py`, CLI flags, GUI tab).
- `deliverables/02-jira/user-stories.md` (for the "who/why" framing).
- `deliverables/04-design/*.md` (for the "how" framing, simplified for an end-user audience).

## Outputs
- Root `README.md` — new "🔐 Encrypted Local Vault" section under Key Features, new `--vault-*`
  examples under CLI Usage, and an updated Project Architecture tree.
- `deliverables/08-documentation/FRD.md` — the formal Functional Requirements Document: scope,
  functional requirements (FR-1..FR-n), non-functional requirements, and traceability back to
  the user stories and test cases.

## Human-in-the-loop gate
Documentation accuracy is spot-checked by a human against the running app before being treated
as final — recorded inline at the bottom of `deliverables/08-documentation/FRD.md`.

## Adaptation note
The reference flow assumes documentation is published to Confluence alongside the design docs.
Here, end-user docs live in the root `README.md` (where a real user would look) and the formal
FRD lives under `.codemie/deliverables/08-documentation/`, giving both audiences (end users vs.
requirements-traceability reviewers) a version suited to them.
