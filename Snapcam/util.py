from pprint import PrettyPrinter
from sys import stderr as STDERR
from termcolor import colored
import typing

pp = PrettyPrinter(indent=4).pprint
ps = PrettyPrinter(indent=4).pformat


def eprint(errmsg, color: str = "red", do_color: bool = True):
    """Prints `errmsg` to STDERR."""
    if do_color:
        print(colored(ps(errmsg), color, attrs=["bold"]), file=STDERR)
    else:
        print(errmsg, file=STDERR)


def cprint(msg, color: str = "magenta", do_color: bool = True):
    if do_color:
        print(colored(ps(msg), color, attrs=["bold"]))
    else:
        print(msg)


def trunc_bytes_at(
    msg: bytes, delim: bytes = b"{", start: int = 1, occurrence: int = 1
):
    """Truncates bytes starting from a given point at nth occurrence of a
    delimiter."""
    return delim.join(msg[start:].split(delim, occurrence)[:occurrence])
