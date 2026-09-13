-- KeyCraft Vault schema (SQLite)
-- vault_meta holds exactly one row: the PBKDF2 salt and an encrypted
-- verifier token used to check the master password on unlock. The master
-- password itself is never stored.
CREATE TABLE IF NOT EXISTS vault_meta (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    salt BLOB NOT NULL,
    verifier BLOB NOT NULL,
    created_at TEXT NOT NULL
);

-- vault_entries holds the saved passwords. encrypted_password is a Fernet
-- token (base64 text); plaintext passwords are never persisted.
CREATE TABLE IF NOT EXISTS vault_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    username TEXT,
    encrypted_password TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
