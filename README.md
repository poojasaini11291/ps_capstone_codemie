# ✨ KeyCraft - Password Generator & Strength Analyzer

A modern, cryptographically secure desktop and command-line password generator and real-time strength analyzer built with **Python** and **CustomTkinter** for **Windows 11**.

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

---

## 🚀 Getting Started

### Installation

Ensure Python 3.10+ is installed:
```powershell
pip install -r requirements.txt
```

### Running the GUI Application

Simply run:
```powershell
python main.py
```

### Keyboard Shortcuts
- `Ctrl + R` / `Space`: Regenerate password
- `Ctrl + T`: Toggle Dark / Light theme

---

## 💻 CLI Usage

KeyCraft includes a CLI for scripting, terminals, or pipelines:

```powershell
# Generate standard 16-character strong password
python main.py

# Generate 24-character password without ambiguous characters
python main.py --length 24 --exclude-ambiguous

# Generate a 5-word memorable passphrase with dots
python main.py --passphrase --words 5 --separator "."

# Generate a 6-digit PIN
python main.py --pin --length 6

# Generate a batch of 10 passwords
python main.py --length 20 --batch 10

# Generate and copy directly to clipboard
python main.py --length 18 --copy

# Check the strength of any password
python main.py --check "P@ssw0rd123!"

# Output machine-readable JSON
python main.py --length 20 --json
```

---

## 🧪 Running Unit Tests

To run the automated test suite:
```powershell
python -m unittest discover -s tests
```

---

## 📁 Project Architecture

```
CodeMie/
├── main.py                     # Application entry point (GUI / CLI dispatcher)
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── core/
│   ├── __init__.py
│   ├── generator.py            # CSPRNG generator, passphrase & PIN logic
│   ├── strength_checker.py     # Shannon entropy, pattern checks & crack estimator
│   ├── wordlist.py             # Curated EFF Diceware wordlist
│   └── clipboard.py            # Clipboard manager & auto-clear scheduler
├── gui/
│   ├── __init__.py
│   ├── app_window.py           # Main CustomTkinter UI window & tabs
│   └── components/
│       ├── __init__.py
│       ├── password_display.py # Large password box & copy controls
│       ├── strength_meter.py   # Visual progress bar & scorecards
│       ├── options_panel.py    # Sliders, toggles, mode tabs
│       └── history_drawer.py   # Session history & batch modal
├── cli/
│   ├── __init__.py
│   └── cli_runner.py           # CLI argument parsing & runner
└── tests/
    ├── __init__.py
    ├── test_generator.py       # Generator tests
    └── test_strength.py        # Strength analyzer tests
```

