# Skill: Requirement Assistant (Business Analyst persona)

## Role
Analyzes the existing application, identifies gaps against the target enhancement, and produces
a Jira-shaped backlog (epic → user stories → tasks) for human review before any design or code
work begins.

## Inputs
- The existing KeyCraft codebase (`app/core/`, `app/gui/`, `app/cli/`, `app/tests/`, root `README.md`).
- The capstone requirement to add one meaningful enhancement to an existing, intentionally
  limited app.
- Non-functional constraints implied by the app's nature: local-only, no network calls, no
  existing persistence layer, desktop + CLI parity expected for every feature.

## Outputs
1. `deliverables/01-analysis/gaps-and-enhancements.md` — what the app can't do today, and why the
   chosen enhancement (encrypted local vault) is the highest-value gap to close.
2. `deliverables/02-jira/epic.md` — one epic, written as it would appear in a Jira epic panel.
3. `deliverables/02-jira/user-stories.md` — 5 user stories in standard `As a / I want / so that`
   form with acceptance criteria, each with a story-point estimate and priority.
4. `deliverables/02-jira/tasks.md` — the engineering task breakdown under each story.
5. `deliverables/03-plan/implementation-plan.md` — sequencing, dependencies, and the HITL
   checkpoints between stages.

## Human-in-the-loop gate
Per the capstone flow, the backlog this persona produces must be reviewed and approved by a
human before the Design Assistant starts. That approval is recorded inline at the bottom of
`deliverables/02-jira/epic.md` rather than as a separate Jira comment thread, since there is no
live Jira connection this session.

## Adaptation note
The reference document assumes a live Jira project where the BA creates real tickets. Here, the
"Jira project" is simulated as local markdown under `deliverables/02-jira/` with the same
epic/story/task hierarchy and the same fields (priority, estimate, acceptance criteria) a real
Jira ticket would carry, so the artifact is structurally equivalent even though it isn't backed
by a running Jira instance.
