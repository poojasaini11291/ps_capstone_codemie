# Deployment / Local Run Guide — KeyCraft with Encrypted Vault

**Persona:** Deployment Assistant (DevOps) · **Status:** Verified

KeyCraft is distributed as source and run locally — there is no server to deploy to. "Deployment"
here means: install dependencies, verify with tests, then run.

## 1. Install
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r app/requirements.txt
```
`app/requirements.txt` now includes `cryptography>=41.0.0` in addition to the pre-existing
`customtkinter`, `pyperclip`, `pillow`.

## 2. Verify
```powershell
cd app && python -m unittest discover -s tests
```
Expect `Ran 22 tests ... OK` (see `../06-testing/test-execution-report.md` for the full run
including the 9 vault-specific tests).

## 3. Run — GUI
```powershell
python app/main.py
```
Open the new **"🔐 Vault"** tab. On first use, `--vault-init`-equivalent flow runs automatically:
you're prompted to create a vault (master password, min. 8 characters). This creates
`app/data/vault.db` on first save/init — the `app/data/` directory does not exist until then, and is
excluded from git via `.gitignore`.

## 4. Run — CLI
```powershell
python app/main.py --vault-init
python app/main.py --length 20 --vault-add "Demo"
python app/main.py --vault-list
python app/main.py --vault-show 1
python app/main.py --vault-delete 1
```
Each command prompts for the master password interactively via `getpass`. It is never accepted
as a `--flag value` — do not attempt to script it by passing the password on the command line.

## 5. Known environment quirk (not a product bug)
On Windows under Git Bash, piping stdin into a command that calls `getpass.getpass()` (e.g.
`printf '...' | python app/main.py --vault-init`) will hang, because `getpass` reads directly from
the console rather than standard input on Windows. Run vault CLI commands from an interactive
terminal (or the GUI) — this is expected `getpass` behavior, not specific to KeyCraft.

## 6. Post-install checklist
- [ ] `app/data/` is not tracked by git (`git status` shows it untracked/ignored after first use).
- [ ] `cd app && python -m unittest discover -s tests` passes with 0 failures.
- [ ] The GUI's "🔐 Vault" tab creates/unlocks a vault and round-trips a saved password.
- [ ] `app/data/vault.db` is never committed — confirmed via `.gitignore`.

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user) — steps above were actually executed during this
implementation session, not merely written speculatively.
