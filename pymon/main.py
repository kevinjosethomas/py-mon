import argparse
import colorama

from .monitor import Monitor

parser = argparse.ArgumentParser(
    prog="pymon",
)

parser.add_argument(
    "filename", type=str, help="the file to be executed with pymon", metavar="filename"
)


def main():
    colorama.init()
    arguments = parser.parse_args()
    monitor = Monitor(arguments.filename)

    monitor.start()

    try:
        while True:
            cmd = input()
            if cmd == "rs":
                monitor.restart_process()
            elif cmd == "stop":
                monitor.stop()
                break
    except KeyboardInterrupt:
        monitor.stop()

    return


if __name__ == "__main__":
    main()
