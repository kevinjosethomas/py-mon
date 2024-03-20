from colorama import Fore, Style


class Color:
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW + Style.BRIGHT
    RED = Fore.RED
    CYAN = Fore.CYAN


def log(colour, message):
    print(f"{colour}[pymon] {message}{Style.RESET_ALL}")
