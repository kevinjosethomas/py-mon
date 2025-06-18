import fnmatch
import argparse
import subprocess
from .logger import *
from sys import executable
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEvent



class Monitor:
    def _handle_event(self, event: FileSystemEvent):
        """
        Handle the event when a file is modified, created, deleted, or moved.
        """

        for ignore_pattern in self.ignore_patterns:
            if self._matches_pattern(event.src_path, ignore_pattern):
                if self.debug:
                    log(Color.CYAN, f"Ignoring change in {event.src_path}")
                return
        
        if not self.clean:
            log(Color.YELLOW, "restarting due to changes detected...")

            if self.debug:
                log(Color.CYAN, f"{event.event_type} {event.src_path}")

        self.restart_process()
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if the given path matches the pattern.
        """

        return fnmatch.fnmatch(path, pattern)
    
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

        self.watch_items = []
        self.patterns = []
        
        for path_pattern in arguments.watch:
            directory, pattern = self._parse_watch_path(path_pattern)
            self.patterns.append(pattern)
            self.watch_items.append((directory, pattern))

        self.process = None
        
        self.event_handler = PatternMatchingEventHandler(
            patterns=self.patterns,
            ignore_patterns=self.ignore_patterns
        )
        
        self.event_handler.on_modified = self._handle_event
        self.event_handler.on_created = self._handle_event
        self.event_handler.on_deleted = self._handle_event
        self.event_handler.on_moved = self._handle_event

        self.observers = []
        for directory, _ in self.watch_items:
            observer = Observer()
            observer.schedule(self.event_handler, directory, recursive=True)
            self.observers.append(observer)

    def start(self):
        """
        Start the monitor and observers.
        """

        if not self.clean:
            for directory, pattern in self.watch_items:
                log(Color.YELLOW, f"watching {pattern} in {directory}")
                
            if self.ignore_patterns:
                log(Color.YELLOW, f"ignoring patterns: {', '.join(self.ignore_patterns)}")
            
            log(Color.YELLOW, "enter 'rs' to restart or 'stop' to terminate")

        for observer in self.observers:
            observer.start()
            
        self.start_process()

    def stop(self):
        """
        Stop the monitor and observers.
        """

        self.stop_process()
        
        for observer in self.observers:
            observer.stop()
            observer.join()

        if not self.clean:
            log(Color.RED, "terminated process")

    def restart_process(self):
        """
        Restart the process.
        """

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
            self.process.wait()
            self.process = None
