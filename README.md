# ✨ KeyCraft - Password Generator & Strength Analyzer

A  modern, cryptographically secure desktop and command-line password generator and real-time strength analyzer built with **Python** and **CustomTkinter** for **Windows 11**.

---

## 🌟 Key Features

### 1. 🔐 Cryptographically Secure Generation
- **CSPRNG**: Uses Python's standard `secrets` module for cryptographically secure random number generation.
- **Customizable Character Sets**:
  - Uppercase letters (`A-Z`)
  - Lowercase letters (`a-z`)
  - Numeric digits (`0-9`)
  - Special symbols (`!@#$%^&*()_+-=[]{}|;:,.<>?`)
  - Option to **Exclude Ambiguous Characters** (`0`, `O`, `1`, `l`, `I`, `|`) to avoid mistyping.
- **Multiple Generation Modes**:
  - **Random Password**: Granular length slider (4–64 characters) with guaranteed presence of all enabled character pools.
  - **Memorable Passphrase**: Diceware/EFF wordlist passphrase generator with customizable word count (3–8 words), separators (`-`, `.`, `_`, space), and optional random number insertion.
  - **PIN Code**: Digits-only generator (4–16 digits).
- **⚡ Batch Generator**: Generate 5, 10, 20, or 50 passwords at once with 1-click clipboard copy and text file export.

### 2. 📋 One-Click Copy to Clipboard
- Large, high-visibility copy button with instant **"✓ Copied!"** animation.
- Secure clipboard operations with fallback to native OS handlers.
- Session generation history with instant 1-click copy for any previously generated password.

### 3. 🛡️ Real-Time Password Strength Analyzer
- **Dual-Mode Evaluation**:
  - Evaluates generated passwords in real time.
  - Dedicated **"Test Any Password"** interactive tester where users can type or paste any password to inspect its security.
- **Shannon Entropy**: Calculates raw and effective entropy in bits ($E = L \cdot \log_2(N)$).
- **Pattern & Vulnerability Detection**:
  - Blacklist check against common weak passwords (e.g. `password`, `123456`, `admin`).
  - Detection of repeated characters (e.g. `aaaa`).
  - Detection of sequential sequences (e.g. `12345`, `abcdef`).
  - Detection of keyboard spatial walks (e.g. `qwerty`, `asdfgh`).
- **5-Level Color-Coded Meter**:
  - 🔴 **Very Weak** (0–24%)
  - 🟠 **Weak** (25–49%)
  - 🟡 **Fair** (50–69%)
  - 🟢 **Strong** (70–84%)
  - 🟢 **Very Strong** (85–100%)
- **⏳ Offline Crack Time Estimation**: Estimates time needed for a 100 Giga-guess/sec GPU cluster to brute-force the password.
- **Security Checklist & Suggestions**: Live badges indicating uppercase, lowercase, numbers, symbols, length (12+ chars), and pattern safety with actionable tips.

### 4. 🔐 Encrypted Local Vault
- **Master-Password Protected**: A single master password (min. 8 characters) protects the entire vault. The master password itself is never stored — only a PBKDF2-derived-key verifier.
- **Strong Encryption**: Each saved password is encrypted at rest with **Fernet** (AES-128-CBC + HMAC), using a key derived via **PBKDF2-HMAC-SHA256** (200,000 iterations) from the master password and a random per-vault salt.
- **Local SQLite Storage**: Entries (label, optional username, encrypted password, timestamps) are stored in a local SQLite database at `app/data/vault.db` — no cloud sync, no network calls.
- **CRUD from GUI or CLI**: Save the currently generated password under a label (e.g. "Gmail", "Bank"), list saved entries, reveal/copy a password on demand, or delete an entry.

---

## 🚀 Getting Started

### Installation

Ensure Python 3.10+ is installed:
```powershell
pip install -r app/requirements.txt
```

### Running the GUI Application

Simply run:
```powershell
python app/main.py
```

### Keyboard Shortcuts
- `Ctrl + R` / `Space`: Regenerate password
- `Ctrl + T`: Toggle Dark / Light theme

---

## 💻 CLI Usage

KeyCraft includes a CLI for scripting, terminals, or pipelines:

```powershell
# Generate standard 16-character strong password
python app/main.py

# Generate 24-character password without ambiguous characters
python app/main.py --length 24 --exclude-ambiguous

# Generate a 5-word memorable passphrase with dots
python app/main.py --passphrase --words 5 --separator "."

# Generate a 6-digit PIN
python app/main.py --pin --length 6

# Generate a batch of 10 passwords
python app/main.py --length 20 --batch 10

# Generate and copy directly to clipboard
python app/main.py --length 18 --copy

# Check the strength of any password
python app/main.py --check "P@ssw0rd123!"

# Output machine-readable JSON
python app/main.py --length 20 --json

# Initialize a new encrypted vault (prompts for a master password)
python app/main.py --vault-init

# Generate a password and save it into the vault under a label
python app/main.py --length 20 --vault-add "Gmail" --username "alice@example.com"

# List saved vault entries (metadata only — passwords stay encrypted)
python app/main.py --vault-list

# Decrypt and print one saved entry's password by id
python app/main.py --vault-show 1

# Delete a saved entry by id
python app/main.py --vault-delete 1
```

> All `--vault-*` commands prompt for the master password interactively (via `getpass`) — it is never passed as a command-line argument.

---

## 🧪 Running Unit Tests

To run the automated test suite:
```powershell
cd app
python -m unittest discover -s tests
```

---

## 📁 Project Architecture

```
CodeMie/
├── README.md                   # Project documentation
├── app/                        # KeyCraft application code
│   ├── main.py                  # Application entry point (GUI / CLI dispatcher)
│   ├── requirements.txt         # Project dependencies
│   ├── db/
│   │   └── schema.sql            # SQLite DDL for the encrypted vault
│   ├── data/                    # Local vault.db lives here (gitignored)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── generator.py          # CSPRNG generator, passphrase & PIN logic
│   │   ├── strength_checker.py   # Shannon entropy, pattern checks & crack estimator
│   │   ├── wordlist.py           # Curated EFF Diceware wordlist
│   │   ├── clipboard.py          # Clipboard manager & auto-clear scheduler
│   │   └── vault.py              # Encrypted vault: init/unlock/add/list/get/delete
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app_window.py         # Main CustomTkinter UI window & tabs
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── password_display.py # Large password box & copy controls
│   │       ├── strength_meter.py   # Visual progress bar & scorecards
│   │       ├── options_panel.py    # Sliders, toggles, mode tabs
│   │       ├── history_drawer.py   # Session history & batch modal
│   │       └── vault_panel.py      # Vault tab: unlock/create, entry list, save/reveal/delete
│   ├── cli/
│   │   ├── __init__.py
│   │   └── cli_runner.py         # CLI argument parsing & runner
│   └── tests/
│       ├── __init__.py
│       ├── test_generator.py     # Generator tests
│       ├── test_strength.py      # Strength analyzer tests
│       └── test_vault.py         # Vault encryption & CRUD tests
├── .codemie/                    # Capstone SDLC deliverables & persona assistant defs
│   ├── skills/                   # Requirement/Design/Code/Review/Test/Deploy/Docs assistants
│   └── deliverables/              # Analysis, Jira, plan, design, code review, testing, deployment, docs
└── reference_files/             # Original capstone project statement & reference docs
```

