import unittest
import string
from core.generator import (
    PasswordConfig,
    PassphraseConfig,
    generate_password,
    generate_passphrase,
    generate_pin,
    generate_batch,
    AMBIGUOUS_CHARS
)


class TestPasswordGenerator(unittest.TestCase):

    def test_default_password_generation(self):
        pwd = generate_password()
        self.assertEqual(len(pwd), 16)
        # Should contain at least one of each standard character set
        self.assertTrue(any(c in string.ascii_uppercase for c in pwd))
        self.assertTrue(any(c in string.ascii_lowercase for c in pwd))
        self.assertTrue(any(c in string.digits for c in pwd))
        self.assertTrue(any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd))

    def test_custom_lengths(self):
        for length in [8, 12, 24, 48, 64]:
            cfg = PasswordConfig(length=length)
            pwd = generate_password(cfg)
            self.assertEqual(len(pwd), length)

    def test_exclude_ambiguous_characters(self):
        cfg = PasswordConfig(
            length=100,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_symbols=True,
            exclude_ambiguous=True
        )
        pwd = generate_password(cfg)
        for c in pwd:
            self.assertNotIn(c, AMBIGUOUS_CHARS, f"Ambiguous character '{c}' found in password!")

    def test_digits_only(self):
        cfg = PasswordConfig(
            length=12,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=True,
            use_symbols=False
        )
        pwd = generate_password(cfg)
        self.assertEqual(len(pwd), 12)
        self.assertTrue(pwd.isdigit())

    def test_passphrase_generation(self):
        cfg = PassphraseConfig(word_count=5, separator=".", capitalize=True, include_number=False)
        passphrase = generate_passphrase(cfg)
        words = passphrase.split(".")
        self.assertEqual(len(words), 5)
        for w in words:
            self.assertTrue(w[0].isupper())

    def test_pin_generation(self):
        pin = generate_pin(6)
        self.assertEqual(len(pin), 6)
        self.assertTrue(pin.isdigit())

    def test_batch_generation(self):
        cfg = PasswordConfig(length=14)
        batch = generate_batch(cfg, count=10)
        self.assertEqual(len(batch), 10)
        for pwd in batch:
            self.assertEqual(len(pwd), 14)


if __name__ == "__main__":
    unittest.main()

