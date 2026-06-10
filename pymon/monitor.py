import argparse
import threading
import subprocess
from .logger import *
from sys import executable
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEvent

# Noise that should never trigger a restart, regardless of watch patterns
DEFAULT_IGNORE_PATTERNS = [
    "*__pycache__*",
    "*.pyc",
    "*.pyo",
    "*/.git",
    "*/.git/*",
]

# Milliseconds to wait after the last detected change before restarting,
# so editor save sequences (create + modify + move) trigger one restart
DEFAULT_DELAY_MS = 250


class Monitor:
    def _handle_event(self, event: FileSystemEvent):
        """
        Handle the event when a file is modified, created, deleted, or moved.
        Restarts are debounced so a burst of events causes a single restart.
        """

        if self.debug and not self.clean:
            log(Color.CYAN, f"{event.event_type} {event.src_path}")

        with self._timer_lock:
            if self._restart_timer:
                self._restart_timer.cancel()
            self._restart_timer = threading.Timer(self.delay, self._restart_after_change)
            self._restart_timer.daemon = True
            self._restart_timer.start()

    def _restart_after_change(self):
        with self._timer_lock:
            self._restart_timer = None

        if not self.clean:
            log(Color.YELLOW, "restarting due to changes detected...")

        self.restart_process()

    def _parse_watch_path(self, path_pattern: str) -> tuple[str, str]:
        """
        Parse a path pattern like 'src/*.py' to extract directory and pattern.
        Returns (directory_to_watch, file_pattern)
        """

        path = Path(path_pattern)

        if any(char in str(path) for char in '*?[]'):
            parts = path.parts
            pattern_index = 0

            for i, part in enumerate(parts):
                if any(char in part for char in '*?[]'):
                    pattern_index = i
                    break

            if pattern_index > 0:
                directory = str(Path(*parts[:pattern_index]))
                pattern = str(Path(*parts[pattern_index:]))
            else:
                directory = '.'
                pattern = path_pattern

            if not directory:
                directory = '.'

            return directory, pattern
        else:
            return path_pattern, '*'

    def __init__(self, arguments: argparse.Namespace):
        self.command = arguments.command
        self.debug = arguments.debug
        self.clean = arguments.clean
        self.exec_mode = arguments.exec
        self.ignore_patterns = arguments.ignore
        self.delay = getattr(arguments, "delay", DEFAULT_DELAY_MS) / 1000

        self.watch_items = []

        for path_pattern in arguments.watch:
            directory, pattern = self._parse_watch_path(path_pattern)
            self.watch_items.append((directory, pattern))

        missing = [directory for directory, _ in self.watch_items if not Path(directory).is_dir()]
        if missing:
            for directory in missing:
                log(Color.RED, f"cannot watch '{directory}': directory does not exist")
            raise SystemExit(1)

        self.process = None
        self._restart_timer = None
        self._timer_lock = threading.Lock()
        self._process_lock = threading.Lock()

        # One handler per watch item so each directory only reacts to its
        # own patterns instead of every pattern from every -w flag
        self.observer = Observer()
        self.event_handlers = []

        for directory, pattern in self.watch_items:
            handler = PatternMatchingEventHandler(
                patterns=[pattern],
                ignore_patterns=self.ignore_patterns + DEFAULT_IGNORE_PATTERNS,
            )

            handler.on_modified = self._handle_event
            handler.on_created = self._handle_event
            handler.on_deleted = self._handle_event
            handler.on_moved = self._handle_event

            self.event_handlers.append(handler)
            self.observer.schedule(handler, directory, recursive=True)

    def start(self):
        """
        Start the monitor and observer.
        """

        if not self.clean:
            for directory, pattern in self.watch_items:
                log(Color.YELLOW, f"watching {pattern} in {directory}")

            if self.ignore_patterns:
                log(Color.YELLOW, f"ignoring patterns: {', '.join(self.ignore_patterns)}")

            log(Color.YELLOW, "enter 'rs' to restart or 'stop' to terminate")

        self.observer.start()

        self.start_process()

    def stop(self):
        """
        Stop the monitor and observer.
        """

        with self._timer_lock:
            if self._restart_timer:
                self._restart_timer.cancel()
                self._restart_timer = None

        with self._process_lock:
            self.stop_process()

        self.observer.stop()
        self.observer.join()

        if not self.clean:
            log(Color.RED, "terminated process")

    def restart_process(self):
        """
        Restart the process.
        """

        with self._process_lock:
            self.stop_process()
            self.start_process()

    def start_process(self):
        if not self.clean:
            log(Color.GREEN, f"starting {self.command}")

        if self.exec_mode:
            if not self.clean:
                log(Color.GREEN, f"executing: {self.command}")
            self.process = subprocess.Popen(self.command, shell=True)
        else:
            py_command = self.command + (".py" if not self.command.endswith(".py") else "")
            self.process = subprocess.Popen([executable, py_command])

    def stop_process(self):
        """
        Stop the process.
        """

        if self.process:
            self.process.terminate()
            self.process = None
