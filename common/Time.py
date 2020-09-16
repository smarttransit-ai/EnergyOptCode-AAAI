# THIS IS START POINT OF ALL CODES
class Time(object):
    def __init__(self, time_str):
        self.time = time_str
        self.time_only = ""
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.time_in_seconds = 0
        self.valid = True
        self.setup()

    def setup(self):
        if "-" in self.time:
            self.day, self.time_only = self.time.split("-")
        else:
            self.time_only = self.time
        self.hour, self.minute, self.second = self.time_only.split(":")
        self.day = int(self.day)
        self.hour = int(self.hour)
        self.minute = int(self.minute)
        self.second = int(self.second)
        self.time_in_seconds = int(self.day * 86400 +
                                   self.hour * 3600 + self.minute * 60 + self.second)

    def __key__(self):
        key_temp = self.time.replace(":", "")
        return key_temp.replace("-", "_")


def time(seconds):
    return Time(convert_sec_time_str(seconds))


def convert_sec_time_str(seconds):
    day = int(seconds // 86400)
    hour = int((seconds // 3600) % 24)
    minute = int((seconds // 60) % 60)
    second = int((seconds % 3600) % 60)
    str_day = str(int(day))
    str_hour = str(int(hour)) if hour > 9 else "0" + str(int(hour))
    str_min = str(int(minute)) if minute > 9 else "0" + str(int(minute))
    str_sec = str(int(second)) if second > 9 else "0" + str(int(second))
    if day == 0:
        time_str = str_hour + ":" + str_min + ":" + str_sec
    else:
        time_str = str_day + "-" + str_hour + ":" + str_min + ":" + str_sec
    return time_str


def diff(first_time, second_time):
    diff_seconds = first_time.time_in_seconds - second_time.time_in_seconds
    if diff_seconds < 0:
        time_diff = Time("00:00:00")
        time_diff.valid = False
    else:
        time_diff = time(diff_seconds)
    return time_diff


def add(first_time, second_time):
    return time(first_time.time_in_seconds + second_time.time_in_seconds)


def t_equals(first_time, second_time):
    return first_time.time_in_seconds == second_time.time_in_seconds


def t_less_than(first_time, second_time):
    return first_time.time_in_seconds < second_time.time_in_seconds


def t_less_or_eq(first_time, second_time):
    return first_time.time_in_seconds <= second_time.time_in_seconds


def t_greater_than(first_time, second_time):
    return first_time.time_in_seconds > second_time.time_in_seconds


def t_greater_or_eq(first_time, second_time):
    return first_time.time_in_seconds >= second_time.time_in_seconds

# SAMPLE TESTING

# print(t_equals(time(0), time(0)))
# print(t_less_or_eq(time(0), time(0)))
# print(t_greater_or_eq(time(1), time(1)))
# print(t_less_than(time(0), time(1)))
# print(t_greater_than(time(2), time(1)))
