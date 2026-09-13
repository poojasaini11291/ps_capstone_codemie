import math
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# Top common weak passwords for instant blacklist detection
COMMON_WEAK_PASSWORDS = {
    "password", "123456", "12345678", "1234", "qwerty", "12345", "dragon", "pussy",
    "baseball", "football", "letmein", "monkey", "shadow", "master", "666666",
    "welcome", "login", "admin", "princess", "solo", "superman", "starwars",
    "iloveyou", "test", "testing", "trustno1", "secret", "default", "access",
    "pass1234", "password123", "abc123", "111111", "000000", "hunter2",
    "charlie", "donald", "killer", "sunshine", "freedom", "matrix", "michael",
    "jordan", "harley", "robert", "thomas", "daniel", "liverpool", "arsenal"
}

# Keyboard spatial walks
KEYBOARD_WALKS = [
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "poiuytrewq", "lkjhgfdsa", "mnbvcxz",
    "1234567890", "0987654321",
    "qazwsxedcrfvtgbyhnujmikolp"
]


@dataclass
class StrengthReport:
    password: str
    length: int = 0
    entropy_bits: float = 0.0
    score: int = 0  # 0 to 100
    level: str = "Very Weak"  # "Very Weak", "Weak", "Fair", "Strong", "Very Strong"
    color: str = "#f85149"
    progress_val: float = 0.0  # 0.0 to 1.0
    estimated_crack_time: str = "Instantly"
    
    # Feature flags
    has_lowercase: bool = False
    has_uppercase: bool = False
    has_digits: bool = False
    has_symbols: bool = False
    is_common: bool = False
    has_repeated_chars: bool = False
    has_sequential_chars: bool = False
    has_keyboard_walk: bool = False
    
    # Actionable guidance
    suggestions: List[str] = field(default_factory=list)
    warning: Optional[str] = None


def calculate_entropy(password: str) -> float:
    """Calculate Shannon entropy in bits for the password."""
    if not password:
        return 0.0

    pool_size = 0
    if re.search(r"[a-z]", password):
        pool_size += 26
    if re.search(r"[A-Z]", password):
        pool_size += 26
    if re.search(r"[0-9]", password):
        pool_size += 10
    if re.search(r"[^a-zA-Z0-9]", password):
        pool_size += 32

    if pool_size == 0:
        return 0.0

    return len(password) * math.log2(pool_size)


def format_crack_time(entropy_bits: float) -> str:
    """
    Estimate time to crack based on a modern high-speed offline GPU cluster
    testing ~100 billion (10^11) guesses per second.
    """
    if entropy_bits <= 0:
        return "Instantly"

    # Total combinations = 2^entropy
    combinations = 2 ** entropy_bits
    guesses_per_sec = 100_000_000_000  # 100 Giga-guesses/sec

    # Average cracking time is combinations / (2 * guesses_per_sec)
    seconds = combinations / (2 * guesses_per_sec)

    if seconds < 1:
        return "Instantly"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours"
    elif seconds < 86400 * 30:
        return f"{int(seconds / 86400)} days"
    elif seconds < 86400 * 365:
        return f"{int(seconds / (86400 * 30))} months"
    elif seconds < 86400 * 365 * 100:
        return f"{int(seconds / (86400 * 365))} years"
    elif seconds < 86400 * 365 * 1000:
        return f"{int(seconds / (86400 * 365 * 100))} centuries"
    elif seconds < 86400 * 365 * 1_000_000:
        return f"{int(seconds / (86400 * 365 * 1000)):,} millennia"
    else:
        return "Trillions of years"


def check_password_strength(password: str) -> StrengthReport:
    """
    Comprehensive password security & strength analyzer.
    Evaluates entropy, character set diversity, repetition, dictionary matches,
    and sequence patterns.
    """
    report = StrengthReport(password=password, length=len(password))

    if not password:
        report.suggestions.append("Enter or generate a password to analyze its strength.")
        return report

    # 1. Character set detection
    report.has_lowercase = bool(re.search(r"[a-z]", password))
    report.has_uppercase = bool(re.search(r"[A-Z]", password))
    report.has_digits = bool(re.search(r"[0-9]", password))
    report.has_symbols = bool(re.search(r"[^a-zA-Z0-9]", password))

    # 2. Entropy calculation
    report.entropy_bits = calculate_entropy(password)

    # 3. Pattern checks
    clean_lower = password.lower()

    # Common weak blacklist
    if clean_lower in COMMON_WEAK_PASSWORDS:
        report.is_common = True
        report.warning = "This is a commonly used weak password!"

    # Repetitive characters (e.g. 'aaaa', '1111')
    if re.search(r"(.)\1\1", password):
        report.has_repeated_chars = True

    # Sequential characters (e.g. '1234', 'abcd')
    for i in range(len(password) - 2):
        chunk = password[i:i+3]
        if len(chunk) == 3:
            c1, c2, c3 = ord(chunk[0]), ord(chunk[1]), ord(chunk[2])
            if (c2 == c1 + 1 and c3 == c2 + 1) or (c2 == c1 - 1 and c3 == c2 - 1):
                report.has_sequential_chars = True
                break

    # Keyboard walks
    for walk in KEYBOARD_WALKS:
        for i in range(len(walk) - 3):
            sub = walk[i:i+4]
            if sub in clean_lower:
                report.has_keyboard_walk = True
                break

    # 4. Scoring Algorithm (0 - 100)
    score = 0

    # Length points (up to 40)
    length = len(password)
    if length >= 16:
        score += 40
    elif length >= 12:
        score += 30
    elif length >= 8:
        score += 15
    elif length >= 6:
        score += 5
    else:
        score += 0

    # Character variety points (up to 35)
    variety_count = sum([report.has_lowercase, report.has_uppercase, report.has_digits, report.has_symbols])
    if variety_count == 4:
        score += 35
    elif variety_count == 3:
        score += 25
    elif variety_count == 2:
        score += 12
    elif variety_count == 1:
        score += 4

    # Entropy scaling (up to 25)
    if report.entropy_bits >= 80:
        score += 25
    elif report.entropy_bits >= 60:
        score += 18
    elif report.entropy_bits >= 45:
        score += 10
    elif report.entropy_bits >= 30:
        score += 5

    # Penalties
    if report.is_common:
        score = min(score, 10)
    if report.has_repeated_chars:
        score = max(0, score - 15)
    if report.has_sequential_chars:
        score = max(0, score - 15)
    if report.has_keyboard_walk:
        score = max(0, score - 15)
    if length < 8:
        score = min(score, 25)

    score = max(0, min(100, score))
    report.score = score
    report.progress_val = score / 100.0

    # 5. Level & Color determination
    if score < 25:
        report.level = "Very Weak"
        report.color = "#f85149"  # Red
    elif score < 50:
        report.level = "Weak"
        report.color = "#f0883e"  # Orange
    elif score < 70:
        report.level = "Fair"
        report.color = "#d29922"  # Yellow/Amber
    elif score < 85:
        report.level = "Strong"
        report.color = "#3fb950"  # Green
    else:
        report.level = "Very Strong"
        report.color = "#2ea043"  # Emerald / Dark Green

    # Crack time estimation
    # If heavily penalized by dictionary/pattern, crack time is near-instant
    effective_entropy = report.entropy_bits
    if report.is_common:
        effective_entropy = 10
    elif report.has_keyboard_walk or report.has_sequential_chars:
        effective_entropy = max(10.0, effective_entropy - 25.0)

    report.estimated_crack_time = format_crack_time(effective_entropy)

    # 6. Actionable Suggestions
    if length < 12:
        report.suggestions.append("Increase length to at least 12–16 characters for robust security.")
    if not report.has_uppercase:
        report.suggestions.append("Add uppercase letters (A-Z) to increase character diversity.")
    if not report.has_lowercase:
        report.suggestions.append("Add lowercase letters (a-z).")
    if not report.has_digits:
        report.suggestions.append("Include numerical digits (0-9).")
    if not report.has_symbols:
        report.suggestions.append("Add special symbols (!@#$%^&*) to significantly boost entropy.")
    if report.has_repeated_chars:
        report.suggestions.append("Avoid repeating the same character 3+ times in a row.")
    if report.has_sequential_chars:
        report.suggestions.append("Avoid sequential character runs like '123' or 'abc'.")
    if report.has_keyboard_walk:
        report.suggestions.append("Avoid keyboard walk patterns like 'qwerty' or 'asdf'.")
    if report.is_common:
        report.suggestions.append("Do not use easily guessable dictionary or default passwords.")

    if not report.suggestions and score >= 80:
        report.suggestions.append("Excellent! This password provides maximum cryptographic security.")

    return report

