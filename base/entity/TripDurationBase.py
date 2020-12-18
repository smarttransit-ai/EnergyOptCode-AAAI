class TripDurationBase(object):
    def __init__(self, start, end):
        self.start_time = start
        self.end_time = end

    def start_s(self):
        if self.start_time is not None:
            return self.start_time.time_in_seconds
        else:
            raise ValueError("start time is not specified")

    def end_s(self):
        if self.end_time is not None:
            return self.end_time.time_in_seconds
        else:
            raise ValueError("end time is not specified")
