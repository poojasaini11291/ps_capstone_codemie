"""
KAN-13 unit tests: auto-clear clipboard — default OFF, GUI callback, CLI flags.

These tests focus on the KAN-13 acceptance criteria that were not already
covered by test_clipboard.py or test_clipboard_autoclear_pytest.py:

  AC2: default is OFF
  AC3: CLI --clipboard-autoclear enables it; no flag → stays off
  AC1/AC4: copy_with_autoclear fires callback when clipboard clears
"""
import pytest
from unittest.mock import Mock, patch

from core import clipboard
from cli.cli_runner import run_cli


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_clipboard_state():
    """Restore module-level state after every test."""
    prev_enabled = clipboard.get_autoclear_enabled()
    prev_delay = clipboard.get_autoclear_delay()
    yield
    clipboard.set_autoclear_enabled(prev_enabled)
    clipboard.set_autoclear_delay(prev_delay)


# ---------------------------------------------------------------------------
# AC2: default is OFF
# ---------------------------------------------------------------------------

def test_module_default_autoclear_is_off():
    """The hard-coded initial value of _autoclear_enabled must be False."""
    import importlib, sys
    # Reload the module from a clean state by temporarily removing it from
    # sys.modules, then re-importing, so we see the true module-level default.
    mod_name = "core.clipboard"
    original_mod = sys.modules.pop(mod_name, None)
    try:
        import core.clipboard as fresh
        assert fresh._autoclear_enabled is False, (
            "KAN-13 requires auto-clear default to be OFF"
        )
    finally:
        if original_mod is not None:
            sys.modules[mod_name] = original_mod
        elif mod_name in sys.modules:
            del sys.modules[mod_name]
        import importlib
        importlib.import_module(mod_name)


# ---------------------------------------------------------------------------
# AC3: CLI — --clipboard-autoclear flag enables; omitting it leaves OFF
# ---------------------------------------------------------------------------

@patch("builtins.print")
@patch("core.clipboard.copy_to_clipboard", return_value=True)
def test_cli_autoclear_off_by_default(mock_copy, mock_print):
    """Omitting --clipboard-autoclear leaves auto-clear disabled."""
    with patch("core.clipboard.schedule_auto_clear_clipboard") as mock_sched:
        run_cli(["--copy"])
    mock_sched.assert_not_called()


@patch("builtins.print")
@patch("core.clipboard.copy_to_clipboard", return_value=True)
def test_cli_autoclear_flag_enables_scheduling(mock_copy, mock_print):
    """--clipboard-autoclear causes schedule_auto_clear_clipboard to be called."""
    with patch("core.clipboard.schedule_auto_clear_clipboard") as mock_sched:
        run_cli(["--copy", "--clipboard-autoclear"])
    mock_sched.assert_called_once()


@patch("builtins.print")
@patch("core.clipboard.copy_to_clipboard", return_value=True)
def test_cli_autoclear_seconds_sets_delay(mock_copy, mock_print):
    """--clipboard-autoclear-seconds N configures the delay."""
    with patch("core.clipboard.schedule_auto_clear_clipboard"):
        run_cli(["--copy", "--clipboard-autoclear", "--clipboard-autoclear-seconds", "7"])
    assert clipboard.get_autoclear_delay() == 7


@patch("builtins.print")
@patch("core.clipboard.copy_to_clipboard", return_value=True)
def test_cli_autoclear_message_printed_when_enabled(mock_copy, mock_print):
    """A 'Clipboard will auto-clear in Ns.' message is printed when enabled."""
    with patch("core.clipboard.schedule_auto_clear_clipboard"):
        run_cli(["--copy", "--clipboard-autoclear", "--clipboard-autoclear-seconds", "15"])

    printed = " ".join(str(c) for c in mock_print.call_args_list)
    assert "auto-clear" in printed.lower() or "15" in printed


# ---------------------------------------------------------------------------
# AC1/AC4: copy_with_autoclear — callback fires when clipboard clears
# ---------------------------------------------------------------------------

def _immediate_schedule(delay_seconds, fn):
    fn()
    return Mock()


def test_copy_with_autoclear_callback_invoked_on_clear():
    """callback passed to copy_with_autoclear is called when clipboard clears."""
    clipboard.set_autoclear_enabled(True)
    clipboard.set_autoclear_delay(5)

    callback = Mock()
    clipboard_store = {"value": ""}

    def fake_get():
        return clipboard_store["value"]

    def fake_set(v):
        clipboard_store["value"] = v

    clipboard_store["value"] = "secret"

    with patch("core.clipboard.copy_to_clipboard", return_value=True):
        with patch("core.clipboard._default_clipboard_get", side_effect=fake_get):
            with patch("core.clipboard._default_clipboard_set", side_effect=fake_set):
                with patch("core.clipboard._default_schedule", side_effect=_immediate_schedule):
                    clipboard.copy_with_autoclear("secret", callback=callback)

    callback.assert_called_once()


def test_copy_with_autoclear_no_callback_when_disabled():
    """callback is not invoked when auto-clear is disabled."""
    clipboard.set_autoclear_enabled(False)
    callback = Mock()

    with patch("core.clipboard.copy_to_clipboard", return_value=True):
        clipboard.copy_with_autoclear("secret", callback=callback)

    callback.assert_not_called()


def test_copy_with_autoclear_no_callback_when_delay_zero():
    """callback is not scheduled when delay is 0."""
    clipboard.set_autoclear_enabled(True)
    clipboard.set_autoclear_delay(0)
    callback = Mock()

    with patch("core.clipboard.copy_to_clipboard", return_value=True):
        with patch("core.clipboard.schedule_auto_clear_clipboard") as mock_sched:
            clipboard.copy_with_autoclear("secret", callback=callback)

    mock_sched.assert_not_called()
    callback.assert_not_called()
