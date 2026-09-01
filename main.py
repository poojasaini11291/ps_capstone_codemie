#!/usr/bin/env python3
"""
KeyCraft - Password Generator & Strength Analyzer
Main entry point for GUI and CLI.
"""
import sys


def main():
    cli_flags = {
        "-l", "--length", "--no-upper", "--no-lower", "--no-digits", "--no-symbols",
        "--exclude-ambiguous", "--passphrase", "--words", "--separator", "--pin",
        "-b", "--batch", "-c", "--check", "--copy", "--json", "-h", "--help", "--cli"
    }

    if any(arg in cli_flags for arg in sys.argv[1:]):
        from cli.cli_runner import run_cli
        filtered_args = [arg for arg in sys.argv[1:] if arg != "--cli"]
        sys.exit(run_cli(filtered_args))
    else:
        from gui.app_window import KeyCraftApp
        app = KeyCraftApp()
        app.mainloop()


if __name__ == "__main__":
    main()

