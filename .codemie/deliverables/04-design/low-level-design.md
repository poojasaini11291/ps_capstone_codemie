# Low-Level Design — Encrypted Local Password Vault

**Persona:** Design Assistant (Architect) · **Status:** Approved — this is the exact contract
implemented in `app/core/vault.py` and `app/db/schema.sql`.

## Schema (`app/db/schema.sql`)

```sql
CREATE TABLE IF NOT EXISTS vault_meta (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    salt BLOB NOT NULL,
    verifier BLOB NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vault_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    username TEXT,
    encrypted_password TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

`vault_meta` is constrained to exactly one row (`id = 1`) since one database file = one vault.

## Module contract (`app/core/vault.py`)

```python
PBKDF2_ITERATIONS = 200_000
DEFAULT_DB_PATH = "app/data/vault.db"   # relative to project root

class VaultError(Exception): ...
class VaultNotInitializedError(VaultError): ...
class VaultAlreadyInitializedError(VaultError): ...
class VaultAuthError(VaultError): ...

@dataclass
class VaultEntryMeta:
    id: int; label: str; username: Optional[str]; created_at: str; updated_at: str

@dataclass
class VaultSession:
    db_path: str; _fernet: Fernet

def vault_exists(db_path=DEFAULT_DB_PATH) -> bool
def init_vault(master_password: str, db_path=DEFAULT_DB_PATH) -> None
def unlock_vault(master_password: str, db_path=DEFAULT_DB_PATH) -> VaultSession
def add_entry(session, label: str, password: str, username: Optional[str] = None) -> int
def list_entries(session) -> List[VaultEntryMeta]
def get_entry_password(session, entry_id: int) -> str
def delete_entry(session, entry_id: int) -> bool
```

### Function-level contracts

- **`vault_exists`**: `False` if the file doesn't exist, or exists but `vault_meta` has no rows
  (or the table itself doesn't exist yet — caught via `sqlite3.OperationalError`).
- **`init_vault`**: raises `VaultAlreadyInitializedError` if `vault_exists()` is already `True`.
  Generates `salt = secrets.token_bytes(16)`, derives a key, encrypts the constant
  `VERIFIER_PLAINTEXT = b"keycraft-vault-verify"`, runs the full DDL via
  `conn.executescript()`, inserts the single `vault_meta` row.
- **`unlock_vault`**: raises `VaultNotInitializedError` if no vault exists. Reads `salt`/
  `verifier`, re-derives the key, attempts `fernet.decrypt(verifier)`; raises `VaultAuthError`
  on `InvalidToken` *or* if the decrypted bytes don't match `VERIFIER_PLAINTEXT` exactly (defense
  in depth against any future verifier-format change).
- **`add_entry`**: raises `ValueError` if `label` or `password` is falsy. Encrypts password with
  `session._fernet`, stores as UTF-8 text (Fernet tokens are URL-safe-base64, so this round-trips
  cleanly through a `TEXT` column). Returns `cursor.lastrowid`.
- **`list_entries`**: `SELECT` excludes `encrypted_password` entirely from the shaped result —
  metadata cannot accidentally leak a password even under a future serialization bug, because
  the field is absent from the returned dataclass, not merely unused.
- **`get_entry_password`**: raises `VaultError` if `entry_id` doesn't exist; raises
  `VaultAuthError` (not a generic decode error) on `InvalidToken`, so callers can distinguish
  "wrong vault key" from "no such entry."
- **`delete_entry`**: returns `cursor.rowcount > 0` — `True`/`False`, no exception for a
  nonexistent id (matches KC-105's acceptance criteria: "fails gracefully").

### Key derivation detail

```python
def _derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                      iterations=PBKDF2_ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))
```
The `base64.urlsafe_b64encode` step is required because `Fernet()` expects its key argument in
that exact encoding, not raw derived bytes.

---
## Human-in-the-loop approval
**Reviewed by:** Product owner (user), as part of the overall plan approval.
