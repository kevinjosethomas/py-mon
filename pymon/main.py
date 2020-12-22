import os
import sys
import time
import argparse
import subprocess
from colorama import Fore, Style
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

def main():
    """CLI Command to execute the provided script with pymon"""

    # CLI Argument Parser
    parser = argparse.ArgumentParser(
        prog="pymon",
        description="Executes the provided script with pymon"
    )

    # Adding arguments to the command
    parser.add_argument("filename", type=str, help="The file to execute with pymon", metavar="filename")
    parser.add_argument("--force-kill", action="store_true", default=False, help="Force kills the file instead of terminating it", dest="force_kill")

    # Fetch arguments
    arguments = parser.parse_args()

    global process

    event_handler = PatternMatchingEventHandler(patterns=["*.py"])

    def handle_event(event):

        global process

        print(Fore.GREEN + "[pymon] restarting due to changes..." + Style.RESET_ALL)

        if arguments.force_kill:
            process.kill()
        else:
            process.terminate()

        process = subprocess.Popen([sys.executable, arguments.filename])

    event_handler.on_any_event = handle_event

    observer = Observer()
    observer.schedule(event_handler, os.getcwd(), recursive=True)

    observer.start()

    print(Fore.YELLOW + Style.BRIGHT + "\n[pymon] watching directory" + Style.RESET_ALL)

    process = subprocess.Popen([sys.executable, arguments.filename])
    print(Fore.GREEN + f"[pymon] starting {arguments.filename}" + Style.RESET_ALL)

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
