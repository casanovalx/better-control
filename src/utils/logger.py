import datetime
from enum import Enum
from io import TextIOWrapper
import os
from sys import stderr, stdout
import time
from typing import Dict, Optional

from utils.arg_parser import ArgParse
from utils.pair import Pair
from tools.terminal import term_support_color


class LogLevel(Enum):
    Debug = 3
    Info = 2
    Warn = 1
    Error = 0


def get_current_time():
    now = datetime.datetime.now()
    ms = int((time.time() * 1000) % 1000)
    return f"{now.minute:02}:{now.second:02}:{ms:03}"


class Logger:
    def __init__(self, arg_parser: ArgParse) -> None:
        log_info: Pair[bool, Optional[str]] = Pair(False, None)

        if arg_parser.find_arg(("-l", "--log")):
            log_info.first = True
            log_info.second = arg_parser.option_arg(("-l", "--log"))

        self.__should_log: bool = log_info.first
        self.__log_level: int = (
            int(log_info.second)
            if (log_info.second is not None) and (log_info.second.isdigit())
            else 3
        )
        self.__add_color: bool = term_support_color()
        self.__log_file_name: str = (
            log_info.second
            if (log_info.second is not None) and (not log_info.second.isdigit())
            else ""
        )
        self.__labels: Dict[LogLevel, Pair[str, str]] = {
            LogLevel.Info: Pair(
                "\x1b[1;37m[\x1b[1;32mINFO\x1b[1;37m]:\x1b[0;0;0m", "[INFO]:"
            ),
            LogLevel.Error: Pair(
                "\x1b[1;37m[\x1b[1;31mERROR\x1b[1;37m]:\x1b[0;0;0m", "[ERROR]:"
            ),
            LogLevel.Debug: Pair(
                "\x1b[1;37m[\x1b[1;36mDEBUG\x1b[1;37m]:\x1b[0;0;0m", "[DEBUG]:"
            ),
            LogLevel.Warn: Pair(
                "\x1b[1:37m[\x1b[1;33mWARNING\x1b[1;37m]:\x1b[0;0;0m", "[WARNING]:"
            ),
        }

        # Initialize log file attribute
        self.__log_file = None

        if self.__log_file_name != "":
            if self.__log_file_name.isdigit():
                digit: int = int(self.__log_file_name)

                if digit in range(4):
                    self.__log_level = digit
                else:
                    self.log(LogLevel.Error, "Invalid log level provided")
            elif not self.__log_file_name.isdigit():
                if not os.path.isfile(self.__log_file_name):
                    self.__log_file = open(self.__log_file_name, "x")
                else:
                    self.__log_file = open(self.__log_file_name, "a")
            else:
                self.log(LogLevel.Error, "Invalid option for argument log")

    def __del__(self):
        if hasattr(self, '_Logger__log_file') and self.__log_file is not None:
            self.__log_file.close()

    def log(self, log_level: LogLevel, message: str):
        """Logs messages to a stream based on user arg

        Args:
            log_level (LogLevel): the log level, which consists of Debug, Info, Warn, Error
            message (str): the log message
        """
        if self.__should_log == False and log_level != LogLevel.Error:
            return

        if self.__log_file_name != "":
            self.__log_to_file(log_level, message)

        label = (
            self.__labels[log_level].first
            if self.__add_color
            else self.__labels[log_level].second
        )

        if log_level == LogLevel.Error:
            print(f"{get_current_time()} {label} {message}", file=stderr)
            exit(1)
        elif log_level == LogLevel.Warn and self.__log_level < 3:
            print(f"{get_current_time()} {label} {message}", file=stdout)
        elif log_level == LogLevel.Info and self.__log_level < 2:
            print(f"{get_current_time()} {label} {message}", file=stdout)
        elif log_level == LogLevel.Debug and self.__log_level < 1:
            print(f"{get_current_time()} {label} {message}", file=stdout)

    def __log_to_file(self, log_level: LogLevel, message: str):
        if not hasattr(self, '_Logger__log_file') or self.__log_file is None:
            return
            
        label = self.__labels[log_level].second

        if log_level == LogLevel.Error:
            print(f"{get_current_time()} {label} {message}", file=self.__log_file)
        else:
            print(f"{get_current_time()} {label} {message}", file=self.__log_file)
