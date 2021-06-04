import argparse
import subprocess
from os import getcwd
from sys import executable

from colorama import Fore, Style, init
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


def main():
    """CLI Command to execute the provided script with pymon"""
    init()

    # CLI Argument Parser
    parser = argparse.ArgumentParser(
        prog="pymon",
        description="Executes the provided script with pymon"
    )

    # Adding arguments to the command
    parser.add_argument("filename", type=str, help="The file to execute with pymon", metavar="filename")
    parser.add_argument("--all", action="store_true", default=False, help="Watch all python Files in directory", dest="all_py")
    parser.add_argument("--force-kill", action="store_true", default=False, help="Force kills the file instead of terminating it", dest="force_kill")

    # Fetch arguments
    arguments = parser.parse_args()
    event_handler = PatternMatchingEventHandler(patterns=['*.py' if arguments.all_py else arguments.filename])

    observer = Observer()
    observer.schedule(event_handler, getcwd(), recursive=True)
    observer.start()

    def _run_file():
        global process
        process = subprocess.Popen([executable, arguments.filename])

    def handle_event(event):
        file_change_type = event.event_type
        print(Fore.GREEN + "[pymon] restarting due to {}...".format(file_change_type) + Style.RESET_ALL)
        process.kill() if arguments.force_kill else process.terminate()
        if file_change_type == 'deleted':
            exit()
        elif file_change_type == 'modified':
            _run_file()

    def _prompt_terminate():
        confirm_terminate = input('Are you sure you want to Terminate?(Y|n) ')
        if confirm_terminate.lower() == 'y':
            observer.stop()

    event_handler.on_any_event = handle_event

    if arguments.all_py:
        print(Fore.YELLOW + Style.BRIGHT + f"[pymon] watching Directory`" + Style.RESET_ALL)
    print(Fore.GREEN + f"[pymon] starting `python {arguments.filename}`" + Style.RESET_ALL)
    _run_file()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        _prompt_terminate()

    observer.join()


if __name__ == "__main__":
    main()
