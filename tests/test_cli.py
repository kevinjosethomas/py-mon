"""Tests for CLI argument parsing."""

import pytest
from unittest.mock import patch

from pymon.main import parser, main
from pymon import __version__


class TestCLIArguments:
    """Tests for command line argument parsing."""

    def test_command_required(self):
        """Should require command argument."""
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_command_parsed(self):
        """Should parse command argument."""
        args = parser.parse_args(["app.py"])
        assert args.command == "app.py"

    def test_watch_default_none(self):
        """Should have None as default watch (merged later)."""
        args = parser.parse_args(["app.py"])
        assert args.watch is None

    def test_watch_single(self):
        """Should parse single watch pattern."""
        args = parser.parse_args(["app.py", "-w", "*.json"])
        assert args.watch == ["*.json"]

    def test_watch_multiple(self):
        """Should parse multiple watch patterns."""
        args = parser.parse_args(["app.py", "-w", "*.py", "-w", "*.json"])
        assert args.watch == ["*.py", "*.json"]

    def test_watch_long_form(self):
        """Should parse --watch long form."""
        args = parser.parse_args(["app.py", "--watch", "src/*.py"])
        assert args.watch == ["src/*.py"]

    def test_ignore_default_empty(self):
        """Should have empty list as default ignore."""
        args = parser.parse_args(["app.py"])
        assert args.ignore == []

    def test_ignore_single(self):
        """Should parse single ignore pattern."""
        args = parser.parse_args(["app.py", "-i", "*.log"])
        assert args.ignore == ["*.log"]

    def test_ignore_multiple(self):
        """Should parse multiple ignore patterns."""
        args = parser.parse_args(["app.py", "-i", "*.log", "-i", "*__pycache__*"])
        assert args.ignore == ["*.log", "*__pycache__*"]

    def test_debug_default_false(self):
        """Should have False as default debug."""
        args = parser.parse_args(["app.py"])
        assert args.debug is False

    def test_debug_flag(self):
        """Should set debug to True with -d flag."""
        args = parser.parse_args(["app.py", "-d"])
        assert args.debug is True

    def test_debug_long_form(self):
        """Should set debug with --debug."""
        args = parser.parse_args(["app.py", "--debug"])
        assert args.debug is True

    def test_clean_default_false(self):
        """Should have False as default clean."""
        args = parser.parse_args(["app.py"])
        assert args.clean is False

    def test_clean_flag(self):
        """Should set clean to True with -c flag."""
        args = parser.parse_args(["app.py", "-c"])
        assert args.clean is True

    def test_exec_default_false(self):
        """Should have False as default exec."""
        args = parser.parse_args(["app.py"])
        assert args.exec is False

    def test_exec_flag(self):
        """Should set exec to True with -x flag."""
        args = parser.parse_args(["app.py", "-x"])
        assert args.exec is True

    def test_combined_flags(self):
        """Should parse multiple flags together."""
        args = parser.parse_args([
            "npm run dev",
            "-x",
            "-d",
            "-w", "*.js",
            "-w", "*.jsx",
            "-i", "node_modules",
        ])
        
        assert args.command == "npm run dev"
        assert args.exec is True
        assert args.debug is True
        assert args.watch == ["*.js", "*.jsx"]
        assert args.ignore == ["node_modules"]

    def test_shell_command_with_exec(self):
        """Should accept shell commands with exec mode."""
        args = parser.parse_args(["python -m http.server", "-x"])
        assert args.command == "python -m http.server"
        assert args.exec is True

    def test_version_flag(self, capsys):
        """Should print version and exit."""
        with pytest.raises(SystemExit) as excinfo:
            parser.parse_args(["--version"])

        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        assert __version__ in out

    def test_version_short_flag(self, capsys):
        """Should print version with short flag and exit."""
        with pytest.raises(SystemExit) as excinfo:
            parser.parse_args(["-V"])

        assert excinfo.value.code == 0
        out = capsys.readouterr().out
        assert __version__ in out


class TestMainLoop:
    """Tests for the main command loop."""

    @patch("pymon.main.Monitor")
    def test_eof_falls_back_to_watch_loop(self, mock_monitor, tmp_path, monkeypatch):
        """Should keep watching (not crash) when stdin is closed."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["pymon", "app.py"])

        with patch("builtins.input", side_effect=EOFError), \
             patch("pymon.main.time.sleep", side_effect=KeyboardInterrupt):
            main()

        mock_monitor.return_value.stop.assert_called_once()

    @patch("pymon.main.Monitor")
    def test_rs_and_stop_commands(self, mock_monitor, tmp_path, monkeypatch):
        """Should restart on 'rs' and terminate on 'stop'."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["pymon", "app.py"])

        with patch("builtins.input", side_effect=["rs", "stop"]):
            main()

        mock_monitor.return_value.restart_process.assert_called_once()
        mock_monitor.return_value.stop.assert_called_once()

