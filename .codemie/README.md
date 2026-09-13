# `.codemie/` — AI-Assisted SDLC Workspace for KeyCraft

This folder is the local stand-in for the CodeMie platform's persona "assistants" and its
Jira/Confluence-backed deliverable tracking, per
`reference_files/codemie-capstone-project-stmt-v01.docx`. No live CodeMie/Jira/Confluence
connection was available for this capstone run, so every artifact that the demo flow expects
those systems to hold is authored here instead, as local markdown, with the same structure and
human-in-the-loop (HITL) review gates the statement describes.

## Why this exists

The capstone statement requires demonstrating an AI-assistant-driven SDLC — Business Analyst,
Architect/Designer, Developer, Code Reviewer, QA, DevOps, and Technical Writer personas, each
with defined inputs/outputs, applied end-to-end to a real enhancement of an **existing**,
intentionally limited application. That application is **KeyCraft** (see repo root `README.md`):
a Python/CustomTkinter password generator and strength analyzer. The enhancement chosen and
implemented against it is an **encrypted local password vault** — a master-password-protected,
SQLite + Fernet/PBKDF2-backed CRUD feature, fully wired into both the CLI and GUI (see
`app/core/vault.py`, `app/cli/cli_runner.py`, `app/gui/components/vault_panel.py`, `app/tests/test_vault.py`).

## Layout

```
.codemie/
├── README.md                  ← you are here
├── skills/                    ← one file per persona "assistant"
│   ├── requirement-assistant.md
│   ├── design-assistant.md
│   ├── code-assistant.md
│   ├── code-review-assistant.md
│   ├── test-assistant.md
│   ├── deployment-assistant.md
│   └── documentation-assistant.md
└── deliverables/               ← what each persona produced, mirroring Jira/Confluence
    ├── 01-analysis/            ← BA: gap analysis vs. capstone requirements
    ├── 02-jira/                ← BA: epic, user stories, tasks (local stand-in for a Jira project)
    ├── 03-plan/                ← BA/PM: implementation plan & sequencing
    ├── 04-design/               ← Architect: architecture, HLD, LLD, wireframes
    ├── 05-code-review/         ← Reviewer: findings on the vault implementation
    ├── 06-testing/             ← QA: Gherkin feature file + execution report
    ├── 07-deployment/          ← DevOps: local run/deploy guide
    └── 08-documentation/       ← Tech Writer: Functional Requirements Document
```

## Mapping to the capstone's 9-step demo flow

| # | Demo flow step | Where it lives here |
|---|---|---|
| 1 | Analyze existing app, identify gaps | `deliverables/01-analysis/gaps-and-enhancements.md` |
| 2 | BA drafts epic/stories in Jira | `deliverables/02-jira/epic.md`, `user-stories.md`, `tasks.md` |
| 3 | Human reviews/approves backlog (HITL) | Approval notes inline in `02-jira/epic.md` |
| 4 | Architect produces design docs in Confluence | `deliverables/04-design/*.md` |
| 5 | Human reviews design (HITL) | Approval notes inline in `04-design/architecture.md` |
| 6 | Developer implements from design, using `claude-code` CLI | `app/core/vault.py`, `app/cli/cli_runner.py`, `app/main.py`, `app/gui/components/vault_panel.py` |
| 7 | Code reviewer assistant reviews the diff | `deliverables/05-code-review/code-review-notes.md` |
| 8 | QA assistant writes & runs tests | `deliverables/06-testing/vault.feature`, `test-execution-report.md`, `app/tests/test_vault.py` |
| 9 | DevOps deploys; Tech writer documents | `deliverables/07-deployment/deployment-guide.md`, `08-documentation/FRD.md`, root `README.md` |

## Adaptations from the reference document

The reference statement's example flow leans on web-app tooling (Selenium/Playwright, JUnit/
TestNG, CI/CD to a server, Jira/Confluence SaaS). KeyCraft is a **Python desktop + CLI app**, so
each skill file below notes explicitly where its tooling diverges from the doc's assumptions
(e.g. `unittest`/`pytest` instead of JUnit/TestNG; manual/local run instead of a server deploy;
local markdown instead of hosted Jira/Confluence).
