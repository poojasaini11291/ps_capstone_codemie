import unittest
from core.strength_checker import (
    check_password_strength,
    calculate_entropy,
    format_crack_time
)


class TestStrengthChecker(unittest.TestCase):

    def test_entropy_calculation(self):
        # 8 lowercase chars: 8 * log2(26) ≈ 37.6 bits
        ent_lower = calculate_entropy("abcdefgh")
        self.assertAlmostEqual(ent_lower, 37.6, delta=0.5)

        # 16 mixed chars: 16 * log2(94) ≈ 104.8 bits
        ent_mixed = calculate_entropy("K9#mX2$vL8@pQ4!z")
        self.assertGreater(ent_mixed, 90.0)

    def test_common_weak_password_detection(self):
        report = check_password_strength("password123")
        self.assertIn(report.level, ["Very Weak", "Weak"])
        self.assertTrue(report.score <= 30)

        report_qwerty = check_password_strength("qwerty")
        self.assertEqual(report_qwerty.level, "Very Weak")
        self.assertTrue(report_qwerty.is_common or report_qwerty.has_keyboard_walk)

    def test_sequential_patterns(self):
        report = check_password_strength("abc123456789")
        self.assertTrue(report.has_sequential_chars)
        self.assertLess(report.score, 60)

    def test_strong_password(self):
        report = check_password_strength("vK9#mX2$vL8@pQ4!")
        self.assertIn(report.level, ["Strong", "Very Strong"])
        self.assertGreaterEqual(report.score, 80)
        self.assertTrue(report.has_uppercase)
        self.assertTrue(report.has_lowercase)
        self.assertTrue(report.has_digits)
        self.assertTrue(report.has_symbols)

    def test_crack_time_formatting(self):
        self.assertEqual(format_crack_time(0), "Instantly")
        self.assertEqual(format_crack_time(10), "Instantly")
        self.assertIn("years", format_crack_time(70) + format_crack_time(85) + format_crack_time(120))


if __name__ == "__main__":
    unittest.main()

