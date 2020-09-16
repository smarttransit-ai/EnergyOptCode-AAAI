import os

from common.configs.global_constants import summary_header_prefix


class FileWriteBase(object):
    def __init__(self, file_name, mode):
        self.__mode = mode
        self.__temp_file_name = file_name + ".temp"
        self.__file = open(file_name, mode)
        self.__temp_file = None
        self.__contents = []

    def __sync(self):
        self.__file.flush()
        os.fsync(self.__file.fileno())

    def write_header(self, header, allow_prefix=False):
        if allow_prefix:
            header = summary_header_prefix + header
        self.write(header)

    def write(self, content):
        if isinstance(content, list):
            content = str(content)[1:-1]
        if not content.endswith("\n"):
            content = content + "\n"
        self.__contents.append(content)
        self.__temp_file = open(self.__temp_file_name, self.__mode)
        self.__temp_file.writelines(self.__contents)
        self.__temp_file.close()
        self.__file.write(content)
        self.__sync()

    def close(self):
        self.__file.close()
        self.__contents.clear()
        if os.path.exists(self.__temp_file_name):
            os.remove(self.__temp_file_name)
