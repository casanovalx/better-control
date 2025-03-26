from ctypes.util import test
from sys import stderr, stdout
from typing import List, Optional, TextIO, Tuple


def eprint(file: Optional[TextIO], *args, **kwargs):
    if file is None:
        file = stdout
    print(*args, file=file, **kwargs)

class ArgParse:
    def __init__(self, args: List[str]) -> None:
        self.args: List[str] = args

    def find_arg(self, arg: Tuple[str, str]) -> bool:
        """tries to find 'arg' inside the argument list

        Args:
            arg (Tuple[str, str]): a tuple containing a short form of the arg, and long form

        Returns:
            bool: true if one of the arg is found, or false
        """
        #? Check for short arg
        for i in self.args:
            if not i.startswith('-'):
                continue

            if i[:2] == "--":
                continue

            if arg[0][1:] in i:
                return True

        #? Check for long arg
        return arg[1] in self.args

    def option_arg(self, arg: Tuple[str, str]) -> Optional[str]:
        """tries to find and return an option from a given argument

        Args:
            arg (Tuple[str, str]): a tuple containing a short form of the arg, and long form

        Returns:
            Optional[str]: the option given or None
        """
        for i, test_arg in enumerate(self.args):
            if not test_arg.startswith('-'):
                continue
            eq_index = -1

            if '=' in test_arg:
                eq_index = test_arg.index('=')
                test_arg = test_arg[:eq_index]

            if '=' not in test_arg:
                if test_arg[:2] != "--" and len(test_arg) > 2:
                    return test_arg[2:]

            if test_arg != arg[0] and test_arg != arg[1]:
                continue

            if eq_index != -1:
                return self.args[i][eq_index + 1:]

            if i + 1 < len(self.args):
                next_arg = self.args[i + 1]
                if not next_arg.startswith('-'):
                    return next_arg
        return None

    def print_help_msg(self, stream: Optional[TextIO]):
        eprint(stream, f"Usage: {self.args[0]} <options>\n")
        eprint(stream, "Options:")
        eprint(stream, f"   -v, --version                   Shows the version of the program")
        eprint(stream, f"   -h, --help                      Prints this message")
        eprint(stream, f"   -B, --battery                   Starts with the battery tab open")
        eprint(stream, f"   -b, --bluetooth                 Starts with the bluetooth tab open")
        eprint(stream, f"   -d, --display                   Starts with the display tab open")
        eprint(stream, f"   -f, --force                     Makes the app force to have all dependencies installed")
        eprint(stream, f"   -V, --volume                    Starts with the volume tab open")
        eprint(stream, f"   -w, --wifi                      Starts with the wifi tab open")
        eprint(stream, f"   -l, --log                       The program will either log to a file if given a file path or output to stdout based on the log level if given a value between 0, 1, 2.")
        eprint(stream, f"                                       0 = debug, info, warning, and error logs will be printed")
        eprint(stream, f"                                       1 = info, warning and error logs will be printed")
        eprint(stream, f"                                       2 = warning, and error logs will be printed")
        eprint(stream, f"                                       3 = only error logs will be printed (default)")

        if stream == stderr:
            exit(1)
        else:
            exit(0)
