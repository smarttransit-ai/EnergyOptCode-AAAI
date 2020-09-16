from common.writer.FileWriteBase import FileWriteBase


class FileAppender(FileWriteBase):
    def __init__(self, file_name):
        super(FileAppender, self).__init__(file_name, "a+")

    def append(self, content):
        self.write(content)
