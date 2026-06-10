import json
import time
import argparse
import colorama
from pathlib import Path

from .monitor import Monitor, DEFAULT_DELAY_MS
from .logger import log, Color
from . import __version__

CONFIG_FILES = [".pymonrc", "pymon.json"]


def load_config():
    """Load configuration from .pymonrc or pymon.json if present."""
    for config_name in CONFIG_FILES:
        config_path = Path(config_name)
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                return config, config_name
            except json.JSONDecodeError as e:
                log(Color.RED, f"Error parsing {config_name}: {e}")
                return {}, None
            except OSError as e:
                log(Color.RED, f"Error reading {config_name}: {e}")
                return {}, None
    return {}, None


def merge_config(args, config):
    """Merge config file settings with command line arguments. CLI takes precedence."""

    if args.watch is None:
        args.watch = config.get("watch", ["*.py"])

    if not args.ignore:
        args.ignore = config.get("ignore", [])

    if not args.debug:
        args.debug = config.get("debug", False)

    if not args.clean:
        args.clean = config.get("clean", False)

    if not args.exec:
        args.exec = config.get("exec", False)

    if args.delay is None:
        args.delay = config.get("delay", DEFAULT_DELAY_MS)

    return args


parser = argparse.ArgumentParser(
    prog="pymon",
)

parser.add_argument(
    "-V",
    "--version",
    action="version",
    version=f"%(prog)s {__version__}",
    help="show the py-mon version and exit",
)

parser.add_argument(
    "command",
    type=str,
    help="the file to be executed or command to run with pymon",
    metavar="command",
)

parser.add_argument(
    "-w",
    "--watch",
    type=str,
    help="paths/patterns to watch (e.g., 'src/*.py', 'data/**/*.json'). use once for each path/pattern. default is '*.py'",
    action="append",
    default=None,
    metavar="path_pattern",
)

parser.add_argument(
    "-d",
    "--debug",
    help="logs detected file changes to the terminal",
    action="store_true",
)

parser.add_argument(
    "-c",
    "--clean",
    help="runs pymon in clean mode (no logs, no commands)",
    action="store_true",
)

parser.add_argument(
    "-i",
    "--ignore",
    type=str,
    help="patterns of files/paths to ignore. use once for each pattern.",
    action="append",
    default=[],
    metavar="patterns",
)

parser.add_argument(
    "-x",
    "--exec",
    help="execute a shell command instead of running a Python file",
    action="store_true",
    default=False,
)

parser.add_argument(
    "--delay",
    type=int,
    help=f"milliseconds to wait after the last file change before restarting (default: {DEFAULT_DELAY_MS})",
    default=None,
    metavar="ms",
)


def main():
    colorama.init()
    arguments = parser.parse_args()

    config, config_name = load_config()
    if config and not arguments.clean:
        log(Color.CYAN, f"using config from {config_name}")
    arguments = merge_config(arguments, config)

    monitor = Monitor(arguments)
    monitor.start()

    try:
        while True:
            if not arguments.clean:
                cmd = input()
                if cmd == "rs":
                    monitor.restart_process()
                elif cmd == "stop":
                    monitor.stop()
                    break
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()

    return


if __name__ == "__main__":
    main()
