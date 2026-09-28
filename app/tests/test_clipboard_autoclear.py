import unittest
from unittest.mock import patch, MagicMock


class TestClipboardAutoClearScheduling(unittest.TestCase):
    """Tests for clipboard auto-clear scheduling behavior (KAN-14)."""

    @patch("core.clipboard.threading.Thread")
    def test_schedule_starts_daemon_thread(self, mock_thread_cls):
        """schedule_auto_clear_clipboard spawns exactly one daemon thread."""
        from core.clipboard import schedule_auto_clear_clipboard

        mock_inst = MagicMock()
        mock_thread_cls.return_value = mock_inst

        schedule_auto_clear_clipboard("secret", delay_seconds=10)

        mock_thread_cls.assert_called_once()
        _, kwargs = mock_thread_cls.call_args
        self.assertTrue(kwargs.get("daemon", False))
        mock_inst.start.assert_called_once()

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_cli_auto_clear_scheduled_by_default(self, _mock_copy, mock_schedule):
        """--copy without --no-clipboard-clear schedules auto-clear with default seconds."""
        from cli.cli_runner import run_cli
        from core.clipboard import CLIPBOARD_CLEAR_DEFAULT_SECONDS

        run_cli(["--copy", "-l", "8"])

        mock_schedule.assert_called_once()
        _args, kwargs = mock_schedule.call_args
        self.assertEqual(kwargs.get("delay_seconds", _args[1] if len(_args) > 1 else None),
                         CLIPBOARD_CLEAR_DEFAULT_SECONDS)

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_cli_no_clipboard_clear_flag_disables_schedule(self, _mock_copy, mock_schedule):
        """--no-clipboard-clear prevents any auto-clear from being scheduled."""
        from cli.cli_runner import run_cli

        run_cli(["--copy", "--no-clipboard-clear", "-l", "8"])

        mock_schedule.assert_not_called()

    @patch("cli.cli_runner.schedule_auto_clear_clipboard")
    @patch("cli.cli_runner.copy_to_clipboard", return_value=True)
    def test_cli_custom_clear_seconds_overrides_default(self, _mock_copy, mock_schedule):
        """--clipboard-clear-seconds overrides the default timeout."""
        from cli.cli_runner import run_cli

        run_cli(["--copy", "--clipboard-clear-seconds", "60", "-l", "8"])

        mock_schedule.assert_called_once()
        _args, kwargs = mock_schedule.call_args
        delay = kwargs.get("delay_seconds", _args[1] if len(_args) > 1 else None)
        self.assertEqual(delay, 60)


if __name__ == "__main__":
    unittest.main()
