from common.Time import Time


class DictObj(object):
    def __init__(self, data_row):
        for key in data_row:
            data = data_row[key].values[0]
            if isinstance(data, float):
                data = round(data, 5)
            data = str(data)
            if key.endswith("_time"):
                data = Time(data)
            self.__dict__[key] = data


class Stop(DictObj):
    def __init__(self, data_row):
        DictObj.__init__(self, data_row)
