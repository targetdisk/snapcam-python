from pprint import PrettyPrinter
import re
import subprocess
from sys import stderr as STDERR
from termcolor import colored
import typing

pp = PrettyPrinter(indent=4).pprint
ps = PrettyPrinter(indent=4).pformat


def lilprint(msg):
  print(msg, end="")


def eprint(errmsg, color: str = "red", do_color: bool = True):
    """Prints `errmsg` to STDERR."""
    if do_color:
        print(colored(ps(errmsg), color, attrs=["bold"]), file=STDERR)
    else:
        print(errmsg, file=STDERR)


def die(errmsg, stat: int = 1):
    """Prints message and exits Python with a status of stat."""
    eprint(errmsg)
    exit(stat)


def cprint(msg, color: str = "magenta", do_color: bool = True):
    if do_color:
        print(colored(ps(msg), color, attrs=["bold"]))
    else:
        print(msg)


def runcmd(args):
    """
    Run a given program/shell command and return its output.

    Error Handling
    ==============
    If the spawned proccess returns a nonzero exit status, it will print the
    program's ``STDERR`` to the running Python iterpreter's ``STDERR``, cause
    Python to exit with a return status of 1.
    """
    proc = subprocess.Popen(
                            args,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                           )

    if proc.wait() == 1:
        print(proc.stdout.read().decode())
        die(proc.stderr.read().decode())

    return proc.stdout.read()


def trunc_bytes_at(
    msg: bytes, delim: bytes = b"{", start: int = 1, occurrence: int = 1
):
    """Truncates bytes starting from a given point at nth occurrence of a
    delimiter."""
    return delim.join(msg[start:].split(delim, occurrence)[:occurrence])


def get_nthreads():
    """Linux only for now..."""
    for line in open("/proc/cpuinfo", mode="r").read().split("\n"):
        words = re.split(r"\s+", line)
        if words[0] == "processor":
            thread_count = int(words[2]) + 1

    return thread_count
