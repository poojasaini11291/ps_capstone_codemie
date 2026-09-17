import os
import sqlite3
import secrets
import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(_PROJECT_ROOT, "data", "vault.db")
SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "db", "schema.sql")

PBKDF2_ITERATIONS = 200_000
VERIFIER_PLAINTEXT = b"keycraft-vault-verify"


class VaultError(Exception):
    """Base exception for all vault operations."""


class VaultNotInitializedError(VaultError):
    """Raised when a vault operation is attempted before init_vault()."""


class VaultAlreadyInitializedError(VaultError):
    """Raised when init_vault() is called on a location that already has a vault."""


class VaultAuthError(VaultError):
    """Raised when the master password fails to unlock the vault."""


@dataclass
class VaultEntryMeta:
    id: int
    label: str
    username: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class VaultSession:
    db_path: str
    _fernet: Fernet


def _derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from the master password via PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def vault_exists(db_path: str = DEFAULT_DB_PATH) -> bool:
    """Return True if an initialized vault database exists at db_path."""
    if not os.path.exists(db_path):
        return False

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM vault_meta")
        return cursor.fetchone()[0] > 0
    except sqlite3.OperationalError:
        return False
    finally:
        conn.close()


def init_vault(master_password: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """Create a new vault database protected by master_password."""
    if vault_exists(db_path):
        raise VaultAlreadyInitializedError("A vault already exists at this location.")

    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    salt = secrets.token_bytes(16)
    fernet = Fernet(_derive_key(master_password, salt))
    verifier = fernet.encrypt(VERIFIER_PLAINTEXT)

    conn = sqlite3.connect(db_path)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.execute(
            "INSERT INTO vault_meta (id, salt, verifier, created_at) VALUES (1, ?, ?, ?)",
            (salt, verifier, _now()),
        )
        conn.commit()
    finally:
        conn.close()


def unlock_vault(master_password: str, db_path: str = DEFAULT_DB_PATH) -> VaultSession:
    """Verify master_password against the stored verifier and return a session for further calls."""
    if not vault_exists(db_path):
        raise VaultNotInitializedError("No vault found at this location. Initialize one first.")

    conn = sqlite3.connect(db_path)
    try:
        salt, verifier = conn.execute("SELECT salt, verifier FROM vault_meta WHERE id = 1").fetchone()
    finally:
        conn.close()

    fernet = Fernet(_derive_key(master_password, salt))

    try:
        decrypted = fernet.decrypt(bytes(verifier))
    except InvalidToken:
        raise VaultAuthError("Incorrect master password.")

    if decrypted != VERIFIER_PLAINTEXT:
        raise VaultAuthError("Incorrect master password.")

    return VaultSession(db_path=db_path, _fernet=fernet)


def add_entry(session: VaultSession, label: str, password: str, username: Optional[str] = None) -> int:
    """Encrypt and store password under label/username. Returns the new entry id."""
    if not label:
        raise ValueError("label is required")
    if not password:
        raise ValueError("password is required")

    encrypted = session._fernet.encrypt(password.encode("utf-8")).decode("utf-8")
    now = _now()

    conn = sqlite3.connect(session.db_path)
    try:
        cursor = conn.execute(
            "INSERT INTO vault_entries (label, username, encrypted_password, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (label, username, encrypted, now, now),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def list_entries(session: VaultSession) -> List[VaultEntryMeta]:
    """List saved entries (metadata only — passwords stay encrypted)."""
    conn = sqlite3.connect(session.db_path)
    try:
        rows = conn.execute(
            "SELECT id, label, username, created_at, updated_at FROM vault_entries "
            "ORDER BY label COLLATE NOCASE"
        ).fetchall()
    finally:
        conn.close()

    return [
        VaultEntryMeta(id=r[0], label=r[1], username=r[2], created_at=r[3], updated_at=r[4])
        for r in rows
    ]


def get_entry_password(session: VaultSession, entry_id: int) -> str:
    """Decrypt and return the plaintext password for entry_id."""
    conn = sqlite3.connect(session.db_path)
    try:
        row = conn.execute(
            "SELECT encrypted_password FROM vault_entries WHERE id = ?", (entry_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise VaultError(f"No vault entry with id {entry_id}.")

    try:
        return session._fernet.decrypt(row[0].encode("utf-8")).decode("utf-8")
    except InvalidToken:
        raise VaultAuthError("Failed to decrypt entry — vault key mismatch or data corruption.")


def delete_entry(session: VaultSession, entry_id: int) -> bool:
    """Delete entry_id. Returns True if a row was deleted."""
    conn = sqlite3.connect(session.db_path)
    try:
        cursor = conn.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
