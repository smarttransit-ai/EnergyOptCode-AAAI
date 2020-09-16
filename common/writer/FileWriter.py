from common.writer.FileWriteBase import FileWriteBase


class FileWriter(FileWriteBase):
    def __init__(self, file_name):
        super(FileWriter, self).__init__(file_name, "w+")
