# -------------------------------------------------------------------------------- #
#                 FETCHING INITIAL DATA AND OTHER BASIC UTILITIES                  #
# -------------------------------------------------------------------------------- #
import os
import shutil
import sys
from enum import Enum


def avg(items):
    return sum(items) / len(items)


def extract(main_dir, file_ending=""):
    _files = []
    for root, dirs, files in os.walk(main_dir):
        for file in files:
            if file.endswith(file_ending):
                __file_path = os.path.join(root, file)
                _files.append(__file_path)
    return _files


def ignore_and_extract(main_dir, file_ending="", ignore_filters=None):
    _files = []
    for root, dirs, files in os.walk(main_dir):
        for file in files:
            if file.endswith(file_ending):
                __file_path = os.path.join(root, file)
                filter_exists = False
                if ignore_filters is not None:
                    for _filter in ignore_filters:
                        if _filter in __file_path:
                            filter_exists = True
                            break
                else:
                    filter_exists = True
                if not filter_exists:
                    _files.append(__file_path)
    return _files


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
    WARN = 'yellow'
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


def convert_loc_string_to_lat_lon(loc_string, deliminator="|"):
    lat, lon = loc_string.split(deliminator)
    return float(lat), float(lon)


def run_function_generic(dump_util, func, args=None):
    try:
        if args is not None:
            func(*args)
        else:
            func()
    except KeyboardInterrupt:
        dump_util.clean_dump()
