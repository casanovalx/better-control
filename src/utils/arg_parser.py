from ctypes.util import test
from math import e
from operator import ne
from sys import stderr, stdout
from typing import Dict, List, Optional, TextIO, Tuple


def sprint(file: Optional[TextIO], *args, **kwargs) -> None:
    """a 'print' statement macro with the 'file' parameter placed on the beggining

    Args:
        file (Optional[TextIO]): the file stream to output to
    """
    if file is None:
        file = stdout
    print(*args, file=file, **kwargs)


class ArgParse:
    def __init__(self, args: List[str]) -> None:
        self.__bin: str = ""
        self.__args: Dict[str, List[str | Dict[str, str]]] = {"long": [], "short": []}
        previous_arg_type: str = ""

        # ? This makes sure that detecting -ai as -a -i works
        # ? and also makes it not dependant on a lot of string operations
        for i, arg in enumerate(args):
            if i == 0:
                self.__bin = arg

            elif arg.startswith("--"):
                self.__args["long"].append(arg[2:])
                previous_arg_type = "long"

            elif arg.startswith("-"):
                self.__args["short"].append(arg[1:])
                previous_arg_type = "short"

            # ? If an arg reaches this statement,
            # ? that means the arg doesnt have a prefix of '-'.
            # ? Which would mean that it is an option
            elif previous_arg_type == "short":
                self.__args["short"].append({"option": arg})
            elif previous_arg_type == "long":
                self.__args["long"].append({"option": arg})

    def find_arg(self, __arg: Tuple[str, str]) -> bool:
        """tries to find 'arg' inside the argument list

        Args:
            arg (Tuple[str, str]): a tuple containing a short form of the arg, and long form

        Returns:
            bool: true if one of the arg is found, or false
        """
        # ? Check for short arg
        for arg in self.__args["short"]:
            if not isinstance(arg, Dict) and __arg[0][1:] in arg:
                return True

        # ? Check for long arg
        for arg in self.__args["long"]:
            if not isinstance(arg, Dict) and __arg[1][2:] == arg:
                return True
        return False

    def option_arg(self, __arg: Tuple[str, str]) -> Optional[str]:
        """tries to find and return an option from a given argument

        Args:
            arg (Tuple[str, str]): a tuple containing a short form of the arg, and long form

        Returns:
            Optional[str]: the option given or None
        """
        # ? Check for short arg
        for i, arg in enumerate(self.__args["short"]):
            if isinstance(arg, Dict):
                continue

            # ? Checks for equal signs, which allow us to check for -lo=a and -o=a
            if "=" in arg:
                eq_index: int = arg.index("=")
                split_arg: Tuple[str, str] = (arg[:eq_index], arg[eq_index + 1 :])

                # ? Check for -lo=a and -o=a
                if (len(split_arg[0]) > 1 and split_arg[0][-1] == __arg[0][1:]) or (
                    len(split_arg[0]) == 1 and split_arg[0][0] == __arg[0][1:]
                ):
                    return split_arg[1]

            # ? Check for -oa
            if len(arg) > 1 and arg[0] == __arg[0][1:]:
                return arg[1:]

            # ? Check for -lo a
            if len(arg) > 1:
                for _, c in enumerate(arg):
                    if c == __arg[0][1:] and i + 1 < len(self.__args["short"]):
                        next_arg = self.__args["short"][i + 1]
                        if isinstance(next_arg, Dict):
                            return next_arg["option"]

            # ? Check for -o a
            if arg == __arg[0][1:] and i + 1 < len(self.__args["short"]):
                next_arg = self.__args["short"][i + 1]

                if isinstance(next_arg, Dict):
                    return next_arg["option"]

        # ? Check for long arg
        for i, arg in enumerate(self.__args["long"]):
            if isinstance(arg, Dict):
                continue

            if "=" in arg:
                eq_index: int = arg.index("=")
                split_arg: Tuple[str, str] = (arg[:eq_index], arg[eq_index + 1 :])

                # ? Check for --option=a
                if split_arg[0] == __arg[1][2:]:
                    return split_arg[1]

            # ? Check for --option a
            if arg == __arg[1][2:] and i + 1 < len(self.__args["long"]):
                next_arg = self.__args["long"][i + 1]

                if isinstance(next_arg, Dict):
                    return next_arg["option"]
        return None

    def arg_print(self, msg: str) -> None:
        sprint(self.__help_stream, msg)

    def print_help_msg(self, stream: Optional[TextIO]):
        self.__help_stream = stream

        self.arg_print(f"Usage: {self.__bin} <options>\n")
        self.arg_print("Options:")
        self.arg_print(
            f"   -v, --version                   Shows the version of the program",
        )
        self.arg_print(f"   -h, --help                      Prints this message")
        self.arg_print(
            f"   -B, --battery                   Starts with the battery tab open",
        )
        self.arg_print(
            f"   -b, --bluetooth                 Starts with the bluetooth tab open",
        )
        self.arg_print(
            f"   -d, --display                   Starts with the display tab open",
        )
        self.arg_print(
            f"   -f, --force                     Makes the app force to have all dependencies installed",
        )
        self.arg_print(
            f"   -V, --volume                    Starts with the volume tab open",
        )
        self.arg_print(
            f"   -w, --wifi                      Starts with the wifi tab open"
        )
        self.arg_print(
            f"   -l, --log                       The program will either log to a file if given a file path,",
        )
        self.arg_print(
            f"                                       or output to stdout based on the log level if given a value between 0, and 3.",
        )

        if stream == stderr:
            exit(1)
        else:
            exit(0)
