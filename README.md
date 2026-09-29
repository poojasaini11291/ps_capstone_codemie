# ✨ KeyCraft — Password Generator & Strength Analyzer

A cryptographically secure desktop and command-line password generator, real-time strength analyzer, and encrypted local password vault built with Python and CustomTkinter for Windows 11.

KeyCraft supports secure password generation, memorable passphrases, PINs, password-strength analysis, batch generation, clipboard operations, and encrypted local password storage.

---

## 1. Executive Summary

| Field | Specification |
|---|---|
| Application Name | KeyCraft |
| Repository Name | CodeMie |
| Service Owner | Pooja Saini |
| Business Impact | Internal — password generation, strength analysis, and local credential management |
| Application Type | Python Desktop GUI and Command-Line Application |
| Description | KeyCraft generates cryptographically secure passwords, passphrases, and PINs. It analyzes password strength and provides an encrypted local vault for managing saved credentials. |
| Target Platform | Windows 11 |
| Operating Model | Local desktop and command-line execution |
| Network Requirement | No network calls are required for the documented vault functionality |

---

## 2. System Architecture & Tech Stack

### Technology Overview

| Component | Specification |
|---|---|
| Programming Language | Python |
| Python Version | Python 3.10 or later |
| Python Runtime | CPython-compatible Python 3.10+ |
| Primary Framework | CustomTkinter |
| GUI Framework | CustomTkinter |
| API Framework | Not Applicable — no REST API is documented |
| Primary Database | SQLite |
| Database Driver | Python SQLite integration; implementation details in app/core/vault.py |
| Cloud Provider | Not Applicable — local application |
| Infrastructure | Windows 11 desktop environment |
| Application Architecture | Modular Python application with GUI, CLI, core business logic, and local database layers |
| Encryption | Fernet encryption with PBKDF2-HMAC-SHA256 key derivation |
| Secure Random Generation | Python secrets module |

### Core Application Modules

| Module | Responsibility |
|---|---|
| app/main.py | Main application entry point and GUI/CLI dispatcher |
| app/core/generator.py | Password, passphrase, and PIN generation |
| app/core/strength_checker.py | Password strength, entropy, and pattern analysis |
| app/core/wordlist.py | Curated EFF Diceware wordlist |
| app/core/clipboard.py | Clipboard management and auto-clear scheduling |
| app/core/vault.py | Encrypted vault operations |
| app/cli/cli_runner.py | CLI argument parsing and execution |
| app/gui/app_window.py | Main desktop GUI |
| app/gui/components/ | Reusable GUI components |
| app/db/schema.sql | SQLite database schema |

### Application Architecture

KeyCraft uses a modular architecture:

1. Presentation layer — CustomTkinter GUI and command-line interface.
2. Core layer — password generation, strength analysis, clipboard operations, and vault logic.
3. Persistence layer — local SQLite database with encrypted password storage.

The application runs locally and does not require a web server or cloud infrastructure.

---

## 3. Integration & Dependencies

### Python Dependencies

Primary dependency configuration:

`app/requirements.txt`

The exact package versions and version constraints are maintained in this file and must be extracted directly from it.

| Dependency / Technology | Purpose |
|---|---|
| CustomTkinter | Desktop GUI |
| Python secrets | Cryptographically secure random generation |
| SQLite | Local vault persistence |
| Fernet | Encryption of stored passwords |
| PBKDF2-HMAC-SHA256 | Master-password-based key derivation |
| Python unittest | Automated testing |

### Dependency Versions

See `app/requirements.txt` for the authoritative declared package versions and constraints.

Do not infer package versions from this README.

### Integration Details

| Field | Specification |
|---|---|
| Upstream Dependencies | Python runtime and declared application dependencies |
| Downstream Consumers | Local GUI users and CLI consumers |
| External APIs | Not Applicable — no external API integration is documented |
| Third-Party Services | Not Applicable to the documented local execution model |
| Internal Integrations | GUI, CLI, core modules, clipboard, and local SQLite vault |
| Dependency File | app/requirements.txt |
| Dependency Manager | pip |
| Virtual Environment | Optional; not required by the documented installation instructions |

### Application Entry Points

| Component | Specification |
|---|---|
| Main Entry Point | app/main.py |
| GUI Entry Point | app/main.py |
| CLI Entry Point | app/main.py |
| CLI Implementation | app/cli/cli_runner.py |
| API Entry Point | Not Applicable |
| Application Port | Not Applicable |

---

## 4. Technical Configuration

### Repository and Runtime

| Field | Specification |
|---|---|
| GitHub Repository | https://github.com/poojasaini11291/ps_capstone_codemie/ |
| Main Branch | main |
| Target Operating System | Windows 11 |
| Minimum Python Version | 3.10 |
| Dependency Installation | pip install -r app/requirements.txt |
| GUI Execution | python app/main.py |
| CLI Execution | python app/main.py with supported CLI arguments |
| Build / Packaging Tool | pip for dependency installation; distributable packaging tool not specified |
| Build Command | Not Specified |
| Configuration Files | app/requirements.txt |
| Database Schema | app/db/schema.sql |
| Local Database | app/data/vault.db |
| Environment Variables | No required environment variables are documented |
| Deployment Pipeline | Not Specified |

### Installation

Install Python 3.10 or later.

Install dependencies:

```bash
pip install -r app/requirements.txt
```

### Run GUI

```bash
python app/main.py
```

### CLI Usage

Generate a password:

```bash
python app/main.py --length 24 --exclude-ambiguous
```

Generate a passphrase:

```bash
python app/main.py --passphrase --words 5 --separator "."
```

Generate a PIN:

```bash
python app/main.py --pin --length 6
```

Generate passwords in a batch:

```bash
python app/main.py --length 20 --batch 10
```

Check password strength:

```bash
python app/main.py --check "P@ssw0rd123!"
```

Generate machine-readable output:

```bash
python app/main.py --length 20 --json
```

Initialize the encrypted vault:

```bash
python app/main.py --vault-init
```

List saved entries:

```bash
python app/main.py --vault-list
```

All vault commands request the master password interactively using getpass.

The master password is not passed as a command-line argument.

### Environment Configuration

No mandatory environment variables are documented for the current local application.

Do not store passwords, API tokens, encryption keys, or other credentials in README.md.

---

## 5. Quality & Compliance

| Field | Specification |
|---|---|
| Unit Test Framework | Python unittest |
| Integration Test Framework | Not Specified |
| GUI / E2E Test Framework | Not Specified |
| Test Directory | app/tests/ |
| Test Execution Command | python -m unittest discover -s tests |
| Code Coverage Tool | Not Specified |
| Code Coverage Goal | Not Specified |
| Security Scanning | Not Specified |
| Logging / Observability | Not Specified |
| CI/CD Pipeline | Not Specified |

### Run Automated Tests

From the repository root:

```bash
cd app
python -m unittest discover -s tests
```

### Test Modules

| Test File | Coverage Area |
|---|---|
| app/tests/test_generator.py | Password generation |
| app/tests/test_strength.py | Password strength analysis |
| app/tests/test_vault.py | Encryption and vault CRUD |

### Security Design

- Uses Python secrets for secure random generation.
- Uses PBKDF2-HMAC-SHA256 with 200,000 iterations for vault key derivation.
- Uses Fernet for encrypted password storage.
- Uses a random per-vault salt.
- Does not store the master password directly.
- Stores encrypted vault entries locally.
- Prompts for the master password interactively.
- Includes password-pattern detection and strength feedback.

These are documented implementation characteristics, not a claim of independent security certification.

---

## 6. Documentation & Resources

| Resource | Reference |
|---|---|
| GitHub Repository | https://github.com/poojasaini11291/ps_capstone_codemie/ |
| README | README.md |
| Dependency Configuration | app/requirements.txt |
| Main Application | app/main.py |
| Database Schema | app/db/schema.sql |
| API Documentation | Not Applicable — no REST API is documented |
| Jira Board | Not Specified |
| Architecture Documentation | README.md — System Architecture & Tech Stack |
| On-Call Rotation | Not Applicable to the documented local application |

### Repository Evidence

The following repository paths provide evidence for the technical profile:

| Source Path | Information |
|---|---|
| README.md | Application purpose, features, installation, architecture, and operational documentation |
| app/requirements.txt | Python dependencies and declared versions |
| app/main.py | Application entry point |
| app/core/generator.py | Password-generation implementation |
| app/core/strength_checker.py | Password-strength analysis |
| app/core/vault.py | Vault and encryption implementation |
| app/core/clipboard.py | Clipboard operations |
| app/cli/cli_runner.py | CLI implementation |
| app/gui/app_window.py | GUI implementation |
| app/db/schema.sql | SQLite database schema |
| app/tests/ | Automated test suite |

---

## 7. Deployment Status

| Field | Specification |
|---|---|
| Current Version | Not Specified |
| Deployment Status | Local execution supported; production release status not specified |
| Deployment Method | Local Python execution |
| Target Platform | Windows 11 |
| Cloud Deployment | Not Applicable |
| Containerization | Not Specified |
| Installation Method | pip install -r app/requirements.txt |
| Execution Command | python app/main.py |
| Last Updated | Generated by EliteA at documentation publication time |
| Documentation Source | GitHub Repository |
| Generated By | EliteA Automated Documentation Sync |

### Deployment Overview

KeyCraft is documented as a locally executed Python desktop and command-line application.

It does not require a hosted web server for its documented functionality.

The application uses local SQLite storage for the encrypted vault.

A packaged installer, production release version, and automated deployment pipeline are not specified in the current documentation.

---

## 8. Key Features

### Cryptographically Secure Generation

- Uses Python's secrets module.
- Supports uppercase, lowercase, numeric, and special characters.
- Supports exclusion of ambiguous characters.
- Generates passwords from 4 to 64 characters.
- Supports memorable passphrases containing 3 to 8 words.
- Generates PINs containing 4 to 16 digits.
- Supports batch generation of 5, 10, 20, or 50 passwords.

### Clipboard Operations

- One-click password copying.
- Copy confirmation animation.
- Native OS clipboard fallback.
- Session generation history.

### Password Strength Analyzer

- Real-time password evaluation.
- Shannon entropy calculation.
- Common-password blacklist checks.
- Repeated-character detection.
- Sequential-pattern detection.
- Keyboard-pattern detection.
- Five-level strength meter.
- Offline crack-time estimation.
- Security checklist and suggestions.

### Encrypted Local Vault

- Master-password-protected storage.
- PBKDF2-derived-key verifier.
- Fernet encryption.
- Local SQLite persistence.
- GUI and CLI vault operations.
- Save, list, reveal, copy, and delete operations.

---

## 9. Project Structure

```text
CodeMie/
├── README.md
├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── db/
│   │   └── schema.sql
│   ├── data/
│   ├── core/
│   │   ├── generator.py
│   │   ├── strength_checker.py
│   │   ├── wordlist.py
│   │   ├── clipboard.py
│   │   └── vault.py
│   ├── gui/
│   │   ├── app_window.py
│   │   └── components/
│   ├── cli/
│   │   └── cli_runner.py
│   └── tests/
│       ├── test_generator.py
│       ├── test_strength.py
│       └── test_vault.py
├── .codemie/
└── reference_files/
```

---

## 10. EliteA Documentation Sync

This repository is used as a source for the EliteA Automated Documentation Sync capstone.

The pipeline performs four stages:

1. Read the master Confluence technical template.
2. Read the GitHub repository and extract technical facts.
3. Populate the template using verified repository evidence.
4. Publish the generated technical profile to Confluence.

### Extraction Rules

- README.md is the primary source for application metadata.
- app/requirements.txt is the authoritative source for dependency versions.
- Source files are authoritative for implementation details.
- Environment variable names may be documented, but secret values must never be published.
- Missing information must be marked Not Specified.
- Confirmed non-applicable components may be marked Not Applicable.
- Technical claims must include supporting repository paths.
- The pipeline must not invent unsupported information.
