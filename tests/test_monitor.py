"""Tests for the Monitor class."""

import pytest
from argparse import Namespace
from unittest.mock import Mock, patch, MagicMock

from pymon.monitor import Monitor


class TestMonitorPathParsing:
    """Tests for path pattern parsing in Monitor."""

    def create_monitor(self, **kwargs):
        """Helper to create a Monitor with default args."""
        defaults = {
            "command": "app.py",
            "watch": ["*.py"],
            "ignore": [],
            "debug": False,
            "clean": False,
            "exec": False,
        }
        defaults.update(kwargs)
        args = Namespace(**defaults)
        
        with patch.object(Monitor, '__init__', lambda self, args: None):
            monitor = Monitor.__new__(Monitor)
            monitor.command = args.command
            monitor.debug = args.debug
            monitor.clean = args.clean
            monitor.exec_mode = args.exec
            monitor.ignore_patterns = args.ignore
        
        return monitor, args

    def test_parse_simple_pattern(self):
        """Should parse simple glob pattern."""
        monitor, _ = self.create_monitor()
        
        directory, pattern = monitor._parse_watch_path("*.py")
        
        assert directory == "."
        assert pattern == "*.py"

    def test_parse_directory_pattern(self):
        """Should parse pattern with directory."""
        monitor, _ = self.create_monitor()
        
        directory, pattern = monitor._parse_watch_path("src/*.py")
        
        assert directory == "src"
        assert pattern == "*.py"

    def test_parse_nested_directory_pattern(self):
        """Should parse pattern with nested directories."""
        monitor, _ = self.create_monitor()
        
        directory, pattern = monitor._parse_watch_path("src/lib/*.py")
        
        assert directory == "src/lib"
        assert pattern == "*.py"

    def test_parse_recursive_pattern(self):
        """Should parse recursive glob pattern."""
        monitor, _ = self.create_monitor()
        
        directory, pattern = monitor._parse_watch_path("src/**/*.py")
        
        assert directory == "src"
        assert pattern == "**/*.py"

    def test_parse_plain_directory(self):
        """Should handle plain directory without glob."""
        monitor, _ = self.create_monitor()
        
        directory, pattern = monitor._parse_watch_path("src")
        
        assert directory == "src"
        assert pattern == "*"

    def test_parse_question_mark_glob(self):
        """Should handle ? glob character."""
        monitor, _ = self.create_monitor()
        
        directory, pattern = monitor._parse_watch_path("src/file?.py")
        
        assert directory == "src"
        assert pattern == "file?.py"

    def test_parse_bracket_glob(self):
        """Should handle [] glob characters."""
        monitor, _ = self.create_monitor()
        
        directory, pattern = monitor._parse_watch_path("src/file[0-9].py")
        
        assert directory == "src"
        assert pattern == "file[0-9].py"


class TestMonitorInitialization:
    """Tests for Monitor initialization."""

    def create_args(self, **kwargs):
        """Helper to create args namespace."""
        defaults = {
            "command": "app.py",
            "watch": ["*.py"],
            "ignore": [],
            "debug": False,
            "clean": False,
            "exec": False,
            "delay": 250,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_init_with_single_watch(self):
        """Should initialize with a single watch pattern."""
        monitor = Monitor(self.create_args())

        assert monitor.command == "app.py"
        assert (".", "*.py") in monitor.watch_items
        assert monitor.debug is False
        assert monitor.clean is False
        assert monitor.exec_mode is False

    def test_init_with_multiple_watch(self, tmp_path, monkeypatch):
        """Should initialize with multiple watch patterns."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config").mkdir()

        args = self.create_args(watch=["*.py", "config/*.json"])
        monitor = Monitor(args)

        assert len(monitor.watch_items) == 2
        assert (".", "*.py") in monitor.watch_items
        assert ("config", "*.json") in monitor.watch_items

    def test_init_with_ignore_patterns(self):
        """Should initialize with ignore patterns."""
        args = self.create_args(ignore=["*.log", "*__pycache__*"])
        monitor = Monitor(args)

        assert monitor.ignore_patterns == ["*.log", "*__pycache__*"]

    def test_init_exec_mode(self):
        """Should initialize in exec mode."""
        args = self.create_args(command="npm run dev", watch=["*.js"], exec=True)
        monitor = Monitor(args)

        assert monitor.exec_mode is True
        assert monitor.command == "npm run dev"

    def test_init_nonexistent_directory_exits(self, tmp_path, monkeypatch, capsys):
        """Should exit with a friendly error when a watch directory is missing."""
        monkeypatch.chdir(tmp_path)

        args = self.create_args(watch=["nonexistent/*.py"])

        with pytest.raises(SystemExit) as excinfo:
            Monitor(args)

        assert excinfo.value.code == 1
        assert "does not exist" in capsys.readouterr().out

    def test_patterns_are_scoped_per_directory(self, tmp_path, monkeypatch):
        """Each watch directory should only react to its own patterns."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "docs").mkdir()

        args = self.create_args(watch=["src/*.py", "docs/*"])
        monitor = Monitor(args)

        src_handler, docs_handler = monitor.event_handlers
        assert src_handler.patterns == ["*.py"]
        assert docs_handler.patterns == ["*"]

    def test_default_ignore_patterns_applied(self):
        """Handlers should ignore __pycache__/.git noise by default."""
        monitor = Monitor(self.create_args(ignore=["*.log"]))

        handler = monitor.event_handlers[0]
        assert "*.log" in handler.ignore_patterns
        assert "*__pycache__*" in handler.ignore_patterns
        assert "*.pyc" in handler.ignore_patterns


class TestMonitorDebounce:
    """Tests for debounced restarts."""

    def create_monitor(self, delay=250):
        args = Namespace(
            command="app.py",
            watch=["*.py"],
            ignore=[],
            debug=False,
            clean=True,
            exec=False,
            delay=delay,
        )
        return Monitor(args)

    def test_burst_of_events_causes_single_restart(self):
        """Several events in quick succession should restart once."""
        import time

        monitor = self.create_monitor(delay=50)
        event = Mock(event_type="modified", src_path="app.py")

        with patch.object(monitor, "restart_process") as mock_restart:
            for _ in range(5):
                monitor._handle_event(event)
            time.sleep(0.3)

        mock_restart.assert_called_once()

    def test_stop_cancels_pending_restart(self):
        """Stopping the monitor should cancel a pending debounced restart."""
        import time

        monitor = self.create_monitor(delay=100)
        monitor.observer.start()
        event = Mock(event_type="modified", src_path="app.py")

        with patch.object(monitor, "restart_process") as mock_restart:
            monitor._handle_event(event)
            monitor.stop()
            time.sleep(0.3)

        mock_restart.assert_not_called()


class TestMonitorProcessManagement:
    """Tests for process start/stop/restart."""

    def create_args(self, **kwargs):
        """Helper to create args namespace."""
        defaults = {
            "command": "app.py",
            "watch": ["*.py"],
            "ignore": [],
            "debug": False,
            "clean": True,  # Use clean mode to suppress output
            "exec": False,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    @patch("pymon.monitor.subprocess.Popen")
    def test_start_process_python_file(self, mock_popen):
        """Should start Python file with python executable."""
        args = self.create_args(command="app.py")
        monitor = Monitor(args)
        
        monitor.start_process()
        
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        assert "app.py" in call_args[0][0][1]

    @patch("pymon.monitor.subprocess.Popen")
    def test_start_process_adds_py_extension(self, mock_popen):
        """Should add .py extension if missing."""
        args = self.create_args(command="app")
        monitor = Monitor(args)
        
        monitor.start_process()
        
        call_args = mock_popen.call_args
        assert "app.py" in call_args[0][0][1]

    @patch("pymon.monitor.subprocess.Popen")
    def test_start_process_exec_mode(self, mock_popen):
        """Should run shell command in exec mode."""
        args = self.create_args(command="npm run dev", exec=True)
        monitor = Monitor(args)
        
        monitor.start_process()
        
        mock_popen.assert_called_once_with("npm run dev", shell=True)

    @patch("pymon.monitor.subprocess.Popen")
    def test_stop_process(self, mock_popen):
        """Should terminate running process."""
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        args = self.create_args()
        monitor = Monitor(args)
        monitor.start_process()
        monitor.stop_process()
        
        mock_process.terminate.assert_called_once()
        assert monitor.process is None

    @patch("pymon.monitor.subprocess.Popen")
    def test_stop_process_when_none(self, mock_popen):
        """Should handle stop when no process is running."""
        args = self.create_args()
        monitor = Monitor(args)
        
        # Should not raise
        monitor.stop_process()
        
        assert monitor.process is None

    @patch("pymon.monitor.subprocess.Popen")
    def test_restart_process(self, mock_popen):
        """Should stop and start process on restart."""
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        args = self.create_args()
        monitor = Monitor(args)
        monitor.start_process()
        monitor.restart_process()
        
        mock_process.terminate.assert_called_once()
        assert mock_popen.call_count == 2

