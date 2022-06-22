import click

import subprocess
from os import getcwd
from typing import Callable
from sys import executable
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEvent


class PymonFileHandler():
    def __init__(
        self, filename: str,
        all: bool = False,
        force_kill: bool = False
    ):
        self.filename = filename
        self.all = all
        self.force_kill = force_kill

    def start_processing(self):
        event_handler = PatternMatchingEventHandler(
            patterns=['*.py' if self.all else self.filename])
        event_handler.on_any_event = self._handle_event

        observer = Observer()
        observer.schedule(event_handler, getcwd(), recursive=True)
        observer.start()

        if self.all:
            click.secho(
                '[pymon] watching Directory', fg='yellow', bold=True)

        click.secho(f'[pymon] starting `python {self.filename}`', fg='green')
        self._run_pyfile()

        PymonFileHandler.handle_terminating(observer.join)

    def _run_pyfile(self):
        self.process = subprocess.Popen([executable, self.filename])

    def _handle_event(self, event: FileSystemEvent):
        click.secho(
            f"[pymon] restarting due to {event.event_type}...", fg='green')

        self.process.kill() if self.force_kill else self.process.terminate()

        if event.event_type == 'deleted':
            exit()
        elif event.event_type == 'modified':
            self._run_pyfile()

    @staticmethod
    def handle_terminating(func: Callable):
        try:
            func()
        except KeyboardInterrupt:
            click.secho('\nTerminating...', fg='red')
