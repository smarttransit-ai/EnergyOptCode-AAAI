import ast
from configparser import ConfigParser

from common.util.common_util import s_print_err


class CustomConfigParserBase(ConfigParser):
    def __init__(self, config_file_name, mode="r"):
        super(CustomConfigParserBase, self).__init__()
        self.__config_file_name = config_file_name
        self.__mode = mode
        if mode == "r" or mode == "r+":
            self.read(config_file_name)

    def write_conf(self):
        conf_file = open(self.__config_file_name, self.__mode)
        self.write(conf_file)
        conf_file.close()

    def __get_elem_val(self, block_name, elem_name, data_type):
        elem = data_type(self.get_block(block_name)[elem_name])
        return elem

    def set_value(self, key, value):
        for block in self.sections():
            if key in self[block]:
                self[block][key] = str(value)

    def set_block(self, block_name, block):
        self[block_name] = block

    def get_config(self):
        return self

    def get_block(self, block_name):
        block = None
        try:
            block = self[block_name]
        except KeyError:
            s_print_err("Configuration block {} not available in {}".format(block_name, self.__config_file_name))
            exit(-1)
        return block

    def literal_eval(self, block_name, elem_name):
        elem = ast.literal_eval(self.get_block(block_name)[elem_name])
        return elem

    def get_int(self, block_name, elem_name):
        return self.__get_elem_val(block_name, elem_name, int)

    def get_float(self, block_name, elem_name):
        return self.__get_elem_val(block_name, elem_name, float)

    def get_str(self, block_name, elem_name):
        return self.__get_elem_val(block_name, elem_name, str)

    def get_date(self, block_name, elem_name):
        date_str = self.get_str(block_name, elem_name)
        from datetime import datetime
        month, day, year = date_str.split("/")
        date = datetime(int(year), int(month), int(day))
        return date


CONFIG_FILE = "config.ini"
main_conf_parser = CustomConfigParserBase(CONFIG_FILE)
