import calendar
import os
import time

from common.writer.FileWriteBase import FileWriteBase


class FileWriter(FileWriteBase):
    def __init__(self, file_name):
        if os.path.exists(file_name):
            ts = calendar.timegm(time.gmtime())
            # create copy based on the timestamp to ensure that previous one is not
            # overwrite with the new one.
            file_name = file_name.replace("_summary.", "_summary_{}.".format(str(ts)))
        super(FileWriter, self).__init__(file_name, "w+")
