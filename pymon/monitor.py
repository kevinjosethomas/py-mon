import os
import subprocess
from sys import executable
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from .logger import *


class Monitor:
    def _handle_event(self, event):
        log(Color.YELLOW, "restarting due to changes detected...")
        self.restart_process()

    def __init__(self, arguments):
        self.filename = arguments.filename + (
            ".py" if not arguments.filename.endswith(".py") else ""
        )
        self.patterns = arguments.patterns
        self.args = arguments.args
        self.watch = arguments.watch

        self.process = None

        self.event_handler = PatternMatchingEventHandler(patterns=self.patterns)
        self.event_handler.on_any_event = self._handle_event

        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.watch, recursive=True)

    def start(self):
        log(Color.YELLOW, f"watching path: {self.watch}")
        log(Color.YELLOW, f"watching patterns: {', '.join(self.patterns)}")
        log(Color.YELLOW, "enter 'rs' to restart or 'stop' to terminate")

        self.observer.start()
        self.start_process()

    def stop(self):
        self.stop_process()
        self.observer.stop()
        self.observer.join()

        log(Color.RED, "terminated process")

    def restart_process(self):
        self.stop_process()
        self.start_process()

    def start_process(self):
        log(Color.GREEN, f"starting {self.filename}")
        self.process = subprocess.Popen([executable, self.filename, *self.args])

    def stop_process(self):
        self.process.terminate()
        self.process = None
