import datetime
from email import message
from enum import _EnumMemberT, Enum
from io import TextIOWrapper
import os
from sys import stderr, stdout
import time
from typing import Dict, Optional, TextIO, Tuple
from pair import Pair
from tools.terminal import term_support_color


class LogLevel(Enum):
    Debug = 2
    Info = 1
    Error = 0

def get_current_time():
    now = datetime.datetime.now()
    ms = int((time.time() * 1000) % 1000)
    return f"{now.minute:02}:{now.second:02}:{ms:03}"

class Logger:
    def __init__(self, pair: Pair[bool, Optional[str]]) -> None:
        self.__should_log: bool = pair.first
        self.__log_level: int = 2
        self.__add_color: bool = term_support_color()
        self.__labels: Dict[LogLevel, Pair[str, str]] = {
            LogLevel.Info: Pair("\e[1;37m[\e[1;32mINFO\e[1;37m]:\e[0;0;0m", "[INFO]:"),
            LogLevel.Error: Pair(
                "\e[1;37m[\e[1;31mERROR\e[1;37m]:\e[0;0;0m", "[ERROR]:"
            ),
            LogLevel.Debug: Pair(
                "\e[1;37m[\e[1;36mDEBUG\e[1;37m]:\e[0;0;0m", "[DEBUG]:"
            ),
        }

        if pair.second is not None:
            if pair.second.isdigit():
                digit: int = int(pair.second)

                if digit in range(3):
                    self.__log_level = digit
                else:
                    self.log(LogLevel.Error, "Invalid log level provided")
            elif pair.second.isalpha():
                if not os.path.isfile(pair.second):
                    self.__log_file: TextIOWrapper = open(pair.second, "x")
                else:
                    self.__log_file: TextIOWrapper = open(pair.second, "a")
            else:
                self.log(LogLevel.Error, "Invalid option for argument log")

    def __del__(self):
        self.__log_file.close()

    def log(self, log_level: LogLevel, message: str):
        if self.__should_log == False and log_level != LogLevel.Error:
            return

        if not self.__log_file.closed:
            self.__log_to_file(log_level, message)

        label = (
            self.__labels[log_level].first
            if self.__add_color
            else self.__labels[log_level].second
        )

        if log_level == LogLevel.Error:
            print(f"{get_current_time()} {label} {message}", file=stderr)
            exit(1)
        elif log_level == LogLevel.Info and self.__log_level < 2:
            print(f"{get_current_time()} {label} {message}", file=stdout)
        elif log_level == LogLevel.Debug and self.__log_level < 1:
            print(f"{get_current_time()} {label} {message}", file=stdout)

    def __log_to_file(self, log_level: LogLevel, message: str):
        label = self.__labels[log_level].second

        if log_level == LogLevel.Error:
            print(f"{get_current_time()} {label} {message}", file=self.__log_file)
        else:
            print(f"{get_current_time()} {label} {message}", file=self.__log_file)
