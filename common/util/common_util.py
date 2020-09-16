# -------------------------------------------------------------------------------- #
#                 FETCHING INITIAL DATA AND OTHER BASIC UTILITIES                  #
# -------------------------------------------------------------------------------- #
import os
import shutil
import sys
from enum import Enum


def create_dir(dir_name):
    if "." in dir_name:
        last_slash = dir_name.rfind("/")
        if last_slash != -1:
            dir_name = dir_name[:last_slash + 1]
    if not os.path.exists(dir_name):
        if "/" not in dir_name:
            os.mkdir(dir_name)
        else:
            try:
                os.makedirs(dir_name)
            except FileExistsError:
                s_print(dir_name + " already exists")


def delete_dir(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)


class PrintTypes(Enum):
    INFO = 'white'
    WARNING = 'yellow'
    ERROR = 'red'


def s_print(content, print_type=PrintTypes.INFO, end=True):
    from termcolor import colored
    content = colored(content, print_type.value)
    if end:
        content += "\n"
    sys.stdout.write(content)


def s_print_warn(content, end=True):
    s_print(content, print_type=PrintTypes.WARN, end=end)


def s_print_err(content, end=True):
    s_print(content, print_type=PrintTypes.ERROR, end=end)


def run_function_generic(dump_util, func, args=None):
    try:
        if args is not None:
            func(*args)
        else:
            func()
    except KeyboardInterrupt:
        dump_util.clean_dump()


def grid_search(func):
    for i in range(1, 11, 1):
        for j in range(1, 11, 1):
            func(i, j)
