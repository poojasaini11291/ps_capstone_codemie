import os
import tempfile
import shutil
import unittest

from core.vault import (
    VaultAuthError,
    VaultNotInitializedError,
    VaultAlreadyInitializedError,
    vault_exists,
    init_vault,
    unlock_vault,
    add_entry,
    list_entries,
    get_entry_password,
    delete_entry
)


class TestVault(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "vault.db")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_vault_does_not_exist_initially(self):
        self.assertFalse(vault_exists(self.db_path))

    def test_init_creates_vault(self):
        init_vault("correct-horse-battery", db_path=self.db_path)
        self.assertTrue(vault_exists(self.db_path))

    def test_init_twice_raises(self):
        init_vault("correct-horse-battery", db_path=self.db_path)
        with self.assertRaises(VaultAlreadyInitializedError):
            init_vault("correct-horse-battery", db_path=self.db_path)

    def test_unlock_without_init_raises(self):
        with self.assertRaises(VaultNotInitializedError):
            unlock_vault("anything", db_path=self.db_path)

    def test_unlock_with_correct_password_succeeds(self):
        init_vault("correct-horse-battery", db_path=self.db_path)
        session = unlock_vault("correct-horse-battery", db_path=self.db_path)
        self.assertEqual(session.db_path, self.db_path)

    def test_unlock_with_wrong_password_raises(self):
        init_vault("correct-horse-battery", db_path=self.db_path)
        with self.assertRaises(VaultAuthError):
            unlock_vault("wrong-password", db_path=self.db_path)

    def test_add_list_get_delete_round_trip(self):
        init_vault("correct-horse-battery", db_path=self.db_path)
        session = unlock_vault("correct-horse-battery", db_path=self.db_path)

        entry_id = add_entry(session, "Gmail", "S3cur3P@ss!", username="alice@example.com")

        entries = list_entries(session)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].id, entry_id)
        self.assertEqual(entries[0].label, "Gmail")
        self.assertEqual(entries[0].username, "alice@example.com")

        decrypted = get_entry_password(session, entry_id)
        self.assertEqual(decrypted, "S3cur3P@ss!")

        self.assertTrue(delete_entry(session, entry_id))
        self.assertEqual(list_entries(session), [])

    def test_delete_nonexistent_entry_returns_false(self):
        init_vault("correct-horse-battery", db_path=self.db_path)
        session = unlock_vault("correct-horse-battery", db_path=self.db_path)
        self.assertFalse(delete_entry(session, 999))

    def test_add_entry_requires_label_and_password(self):
        init_vault("correct-horse-battery", db_path=self.db_path)
        session = unlock_vault("correct-horse-battery", db_path=self.db_path)

        with self.assertRaises(ValueError):
            add_entry(session, "", "somepassword")
        with self.assertRaises(ValueError):
            add_entry(session, "Label", "")

    def test_entries_are_encrypted_at_rest(self):
        init_vault("correct-horse-battery", db_path=self.db_path)
        session = unlock_vault("correct-horse-battery", db_path=self.db_path)
        add_entry(session, "Bank", "PlaintextSecret123")

        with open(self.db_path, "rb") as f:
            raw = f.read()
        self.assertNotIn(b"PlaintextSecret123", raw)


if __name__ == "__main__":
    unittest.main()
