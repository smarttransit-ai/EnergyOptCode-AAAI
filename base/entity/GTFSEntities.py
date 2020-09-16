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


class Shape(DictObj):
    def __init__(self, data_row):
        DictObj.__init__(self, data_row)


class BusTrip(DictObj):
    def __init__(self, data_row):
        DictObj.__init__(self, data_row)
        self.shapes = []
        self.start_pos = None
        self.end_pos = None
        self.start_time = None
        self.end_time = None

    def set_start_and_end(self, start, end):
        self.start_pos = start.stop
        self.end_pos = end.stop
        self.start_time = start.stop_time.arrival_time
        self.end_time = end.stop_time.departure_time

    def set_shapes(self, shapes):
        self.shapes = shapes

    def get_lat_lon(self):
        lat_lon_list = []
        for shape in self.shapes:
            lat_lon = (round(float(shape.shape_pt_lat), 5), round(float(shape.shape_pt_lon), 5))
            lat_lon_list.append(lat_lon)
        return lat_lon_list

    def trip_key(self):
        return round(float(self.start_pos.stop_lat), 5), round(float(self.start_pos.stop_lon), 5), \
               round(float(self.end_pos.stop_lat), 5), round(float(self.end_pos.stop_lon), 5), \
               self.start_time.time_in_seconds


class Stop(DictObj):
    def __init__(self, data_row):
        DictObj.__init__(self, data_row)


class StopTime(DictObj):
    def __init__(self, data_row):
        DictObj.__init__(self, data_row)
