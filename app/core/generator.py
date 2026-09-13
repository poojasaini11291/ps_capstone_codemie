import string
import secrets
from dataclasses import dataclass
from typing import List, Optional
from .wordlist import EFF_WORDLIST


AMBIGUOUS_CHARS = set("0O1lI|`'\"")
SIMILAR_SYMBOLS = set("{}[]()/\\'\"`~,;:.<>")
DEFAULT_SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


@dataclass
class PasswordConfig:
    length: int = 16
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = False
    custom_symbols: str = DEFAULT_SYMBOLS


@dataclass
class PassphraseConfig:
    word_count: int = 4
    separator: str = "-"
    capitalize: bool = True
    include_number: bool = True


@dataclass
class PinConfig:
    length: int = 6


def get_character_pools(config: PasswordConfig) -> tuple[List[str], str]:
    """
    Returns a tuple of:
    1. A list of individual character sets that must be included (at least 1 char each).
    2. A combined string of all allowable characters.
    """
    required_pools = []
    combined_pool = ""

    # Uppercase
    if config.use_uppercase:
        upper = string.ascii_uppercase
        if config.exclude_ambiguous:
            upper = "".join(c for c in upper if c not in AMBIGUOUS_CHARS)
        if upper:
            required_pools.append(upper)
            combined_pool += upper

    # Lowercase
    if config.use_lowercase:
        lower = string.ascii_lowercase
        if config.exclude_ambiguous:
            lower = "".join(c for c in lower if c not in AMBIGUOUS_CHARS)
        if lower:
            required_pools.append(lower)
            combined_pool += lower

    # Digits
    if config.use_digits:
        digits = string.digits
        if config.exclude_ambiguous:
            digits = "".join(c for c in digits if c not in AMBIGUOUS_CHARS)
        if digits:
            required_pools.append(digits)
            combined_pool += digits

    # Symbols
    if config.use_symbols:
        symbols = config.custom_symbols or DEFAULT_SYMBOLS
        if config.exclude_ambiguous:
            symbols = "".join(c for c in symbols if c not in AMBIGUOUS_CHARS)
        if symbols:
            required_pools.append(symbols)
            combined_pool += symbols

    return required_pools, combined_pool


def generate_password(config: Optional[PasswordConfig] = None) -> str:
    """
    Generate a cryptographically secure random password using Python's secrets module.
    Guarantees at least 1 character from each selected pool and securely shuffles results.
    """
    if config is None:
        config = PasswordConfig()

    required_pools, combined_pool = get_character_pools(config)

    # Fallback to lowercase letters if everything was deselected
    if not combined_pool:
        combined_pool = string.ascii_lowercase
        required_pools = [combined_pool]

    length = max(len(required_pools), config.length)

    # Guarantee at least 1 character from each enabled pool
    password_chars = [secrets.choice(pool) for pool in required_pools]

    # Fill the remaining length with random choices from combined pool
    remaining_length = length - len(password_chars)
    password_chars.extend(secrets.choice(combined_pool) for _ in range(remaining_length))

    # Cryptographically secure in-place shuffle
    rng = secrets.SystemRandom()
    rng.shuffle(password_chars)

    return "".join(password_chars)


def generate_passphrase(config: Optional[PassphraseConfig] = None) -> str:
    """
    Generate a memorable Diceware/EFF style passphrase.
    Example: 'Galaxy-Orbit-Frost-9-Beacon'
    """
    if config is None:
        config = PassphraseConfig()

    count = max(2, min(12, config.word_count))
    words = [secrets.choice(EFF_WORDLIST) for _ in range(count)]

    if config.capitalize:
        words = [w.capitalize() for w in words]

    if config.include_number:
        # Insert a random single or two-digit number into one of the slots
        num = str(secrets.randbelow(90) + 10)  # 10-99
        insert_idx = secrets.randbelow(len(words) + 1)
        words.insert(insert_idx, num)

    return config.separator.join(words)


def generate_pin(length: int = 6) -> str:
    """
    Generate a cryptographically secure numeric PIN.
    """
    clean_length = max(3, min(32, length))
    return "".join(secrets.choice(string.digits) for _ in range(clean_length))


def generate_batch(config: PasswordConfig, count: int = 10) -> List[str]:
    """Generate a batch of multiple random passwords."""
    clean_count = max(1, min(100, count))
    return [generate_password(config) for _ in range(clean_count)]

