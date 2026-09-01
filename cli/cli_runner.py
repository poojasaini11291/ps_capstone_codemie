import sys
import json
import argparse
from typing import List, Optional

from core.generator import (
    PasswordConfig,
    PassphraseConfig,
    generate_password,
    generate_passphrase,
    generate_pin,
    generate_batch
)
from core.strength_checker import check_password_strength
from core.clipboard import copy_to_clipboard


def run_cli(args: Optional[List[str]] = None) -> int:
    """CLI runner for KeyCraft Password Generator & Strength Analyzer."""
    parser = argparse.ArgumentParser(
        prog="keycraft",
        description="KeyCraft - Cryptographically Secure Password Generator & Strength Analyzer"
    )

    # Mode arguments
    parser.add_argument("-l", "--length", type=int, default=16, help="Password length (default: 16)")
    parser.add_argument("--no-upper", action="store_true", help="Exclude uppercase letters (A-Z)")
    parser.add_argument("--no-lower", action="store_true", help="Exclude lowercase letters (a-z)")
    parser.add_argument("--no-digits", action="store_true", help="Exclude digits (0-9)")
    parser.add_argument("--no-symbols", action="store_true", help="Exclude special symbols")
    parser.add_argument("--exclude-ambiguous", action="store_true", help="Exclude ambiguous characters (0, O, 1, l, I)")

    # Passphrase mode
    parser.add_argument("--passphrase", action="store_true", help="Generate a memorable passphrase")
    parser.add_argument("--words", type=int, default=4, help="Word count for passphrase (default: 4)")
    parser.add_argument("--separator", type=str, default="-", help="Separator for passphrase words (default: '-')")

    # PIN mode
    parser.add_argument("--pin", action="store_true", help="Generate a numeric PIN")

    # Batch mode
    parser.add_argument("-b", "--batch", type=int, default=1, help="Generate multiple passwords")

    # Strength analyzer mode
    parser.add_argument("-c", "--check", type=str, help="Analyze the strength of a provided password")

    # Utilities
    parser.add_argument("--copy", action="store_true", help="Copy the generated password to clipboard")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    parsed = parser.parse_args(args)

    # 1. Strength Check Mode
    if parsed.check:
        report = check_password_strength(parsed.check)
        if parsed.json:
            out = {
                "password": report.password,
                "length": report.length,
                "score": report.score,
                "level": report.level,
                "entropy_bits": round(report.entropy_bits, 2),
                "estimated_crack_time": report.estimated_crack_time,
                "has_lowercase": report.has_lowercase,
                "has_uppercase": report.has_uppercase,
                "has_digits": report.has_digits,
                "has_symbols": report.has_symbols,
                "is_common": report.is_common,
                "suggestions": report.suggestions,
                "warning": report.warning
            }
            print(json.dumps(out, indent=2))
        else:
            print("=" * 60)
            print(f"  Password Strength Analysis: '{parsed.check}'")
            print("=" * 60)
            print(f" Score       : {report.score}/100 [{report.level.upper()}]")
            print(f" Entropy     : {report.entropy_bits:.2f} bits")
            print(f" Crack Time  : {report.estimated_crack_time}")
            print(f" Diversity   : Upper={report.has_uppercase}, Lower={report.has_lowercase}, Digits={report.has_digits}, Symbols={report.has_symbols}")
            if report.warning:
                print(f"\n [!] WARNING: {report.warning}")
            if report.suggestions:
                print("\n Suggestions:")
                for s in report.suggestions:
                    print(f"   • {s}")
        return 0

    # 2. Passphrase Generation Mode
    if parsed.passphrase:
        cfg = PassphraseConfig(word_count=parsed.words, separator=parsed.separator)
        if parsed.batch > 1:
            passwords = [generate_passphrase(cfg) for _ in range(parsed.batch)]
        else:
            passwords = [generate_passphrase(cfg)]

    # 3. PIN Generation Mode
    elif parsed.pin:
        if parsed.batch > 1:
            passwords = [generate_pin(parsed.length) for _ in range(parsed.batch)]
        else:
            passwords = [generate_pin(parsed.length)]

    # 4. Standard Random Password Mode
    else:
        cfg = PasswordConfig(
            length=parsed.length,
            use_uppercase=not parsed.no_upper,
            use_lowercase=not parsed.no_lower,
            use_digits=not parsed.no_digits,
            use_symbols=not parsed.no_symbols,
            exclude_ambiguous=parsed.exclude_ambiguous
        )
        if parsed.batch > 1:
            passwords = generate_batch(cfg, count=parsed.batch)
        else:
            passwords = [generate_password(cfg)]

    # Output results
    if parsed.copy and passwords:
        copy_to_clipboard(passwords[0])

    if parsed.json:
        results = []
        for pwd in passwords:
            rep = check_password_strength(pwd)
            results.append({
                "password": pwd,
                "length": rep.length,
                "score": rep.score,
                "level": rep.level,
                "entropy_bits": round(rep.entropy_bits, 2),
                "crack_time": rep.estimated_crack_time
            })
        print(json.dumps({"passwords": results}, indent=2))
    else:
        for pwd in passwords:
            rep = check_password_strength(pwd)
            copy_tag = " (Copied to clipboard)" if parsed.copy and len(passwords) == 1 else ""
            print(f"{pwd:<32} [Score: {rep.score}/100 - {rep.level} - {rep.entropy_bits:.1f} bits]{copy_tag}")

    return 0

