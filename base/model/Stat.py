from common.Time import add, diff, time
from common.configs.model_constants import serving, moving, charging
from common.util.common_util import s_print

stat_decorator_char = "="
stat_footer_length = 34
stat_header_length = 32
movements_header_length = 28


class InternalStat(object):
    def __init__(self, duration=time(0), energy_kwh=0, energy_gallon=0, energy_cost=0,
                 electric_count=0, gasoline_count=0):
        self.duration = duration
        self.kwh_energy_consumed = energy_kwh
        self.gallon_energy_consumed = energy_gallon
        self.energy_cost = energy_cost
        self.electric_count = electric_count
        self.gasoline_count = gasoline_count
        self.count = max(electric_count, gasoline_count)

    def copy(self):
        copy_stat = InternalStat()
        copy_stat.duration = self.duration
        copy_stat.kwh_energy_consumed = self.kwh_energy_consumed
        copy_stat.gallon_energy_consumed = self.gallon_energy_consumed
        copy_stat.energy_cost = self.energy_cost
        copy_stat.electric_count = self.electric_count
        copy_stat.gasoline_count = self.gasoline_count
        copy_stat.count = self.count
        return copy_stat

    def map(self, map_stat):
        self.duration = map_stat.duration
        self.kwh_energy_consumed = map_stat.kwh_energy_consumed
        self.gallon_energy_consumed = map_stat.gallon_energy_consumed
        self.energy_cost = map_stat.energy_cost
        self.count = map_stat.count
        self.electric_count = map_stat.electric_count
        self.gasoline_count = map_stat.gasoline_count

    def add(self, stat, force_add=True):
        add_stat = self.copy()
        add_stat.duration = add(stat.duration, add_stat.duration)
        add_stat.kwh_energy_consumed += stat.kwh_energy_consumed
        add_stat.gallon_energy_consumed += stat.gallon_energy_consumed
        add_stat.energy_cost += stat.energy_cost
        add_stat.count += stat.count
        add_stat.electric_count += stat.electric_count
        add_stat.gasoline_count += stat.gasoline_count
        if force_add:
            self.map(add_stat)
            return self
        return add_stat

    def diff(self, stats):
        diff_stat = self.copy()
        for stat in stats:
            diff_stat.duration = diff(diff_stat.duration, stat.duration)
            diff_stat.kwh_energy_consumed = diff_stat.kwh_energy_consumed - stat.kwh_energy_consumed
            diff_stat.gallon_energy_consumed = diff_stat.gallon_energy_consumed - stat.gallon_energy_consumed
            diff_stat.energy_cost = diff_stat.energy_cost - stat.energy_cost
            diff_stat.electric_count = diff_stat.electric_count - stat.electric_count
            diff_stat.gasoline_count = diff_stat.gasoline_count - stat.gasoline_count
            diff_stat.count = diff_stat.count - stat.count
        return diff_stat

    def get_csv_line(self):
        line = self.duration.time + "," + str(self.count) + ","
        line += str(self.kwh_energy_consumed) + ","
        line += str(self.gallon_energy_consumed) + ","
        line += str(self.energy_cost) + ","
        return line

    def get_min_csv_line(self, is_charging=False):
        line = self.duration.time + "," + str(self.count) + ","
        if not is_charging:
            if self.kwh_energy_consumed > 0:
                line += str(self.kwh_energy_consumed) + ","
            elif self.gallon_energy_consumed > 0:
                line += str(self.gallon_energy_consumed) + ","
            else:
                line += "0,"
            if self.energy_cost > 0:
                line += str(self.energy_cost) + ","
            else:
                line += "0,"
        return line

    def print(self, prefix=""):
        # print only when there is an assignment
        if self.duration.time_in_seconds != 0:
            s_print(prefix + " Duration " + self.duration.time)
            s_print(prefix + " Assignments " + str(self.count))
            if self.kwh_energy_consumed > 0:
                s_print(prefix + " EV Assignments " + str(self.electric_count))
                s_print(prefix + " Energy Consumed " + str(round(self.kwh_energy_consumed, 4)) + " kwh")
            if self.gallon_energy_consumed > 0:
                s_print(prefix + " GV Assignments " + str(self.gasoline_count))
                s_print(prefix + " Energy Consumed " + str(round(self.gallon_energy_consumed, 4)) + " gallon(s)")
            if self.energy_cost > 0:
                s_print(prefix + " Energy Cost $" + str(round(self.energy_cost, 4)))


class Stat(object):
    def __init__(self, internal_stat=None, movement_type=serving):
        self.total = InternalStat()
        self.moving = InternalStat()
        self.charging = InternalStat()
        if internal_stat is not None:
            self.total = internal_stat
            if movement_type == moving:
                self.moving = internal_stat
            if movement_type == charging:
                self.charging = internal_stat

    def add_stat(self, stat, movement_type=serving):
        self.total.add(stat.total)
        if movement_type == moving:
            self.moving.add(stat.moving)
        if movement_type == charging:
            self.charging.add(stat.charging)

    def print(self, info=""):
        self.total.print("Total")
        diff_stat = self.total.diff([self.moving, self.charging])
        diff_stat.print("Operating")
        self.moving.print("Moving")
        self.charging.print("Charging")

    def get_csv_line(self):
        line = self.total.get_csv_line()
        diff_stat = self.total.diff([self.moving, self.charging])
        line += diff_stat.get_csv_line()
        line += self.moving.get_csv_line()
        line += self.charging.get_csv_line()
        return line

    def get_min_csv_line(self):
        line = self.total.get_min_csv_line()
        diff_stat = self.total.diff([self.moving, self.charging])
        line += diff_stat.get_min_csv_line()
        line += self.moving.get_min_csv_line()
        line += self.charging.get_min_csv_line(is_charging=True)
        return line


def dict_add(movements, init_movements):
    for key in init_movements:
        value = init_movements[key]
        if isinstance(value, list):
            if key in movements:
                movements[key].extend(value)
            else:
                movements[key] = value
        else:
            if key in movements:
                movements[key].append(value)
            else:
                movements[key] = [value]
    return movements


def print_hf(half_count, char=stat_decorator_char, info=""):
    for i in range(half_count):
        s_print(char, end=False)
    if info != "":
        s_print(" " + info + " ", end=False)
    for i in range(half_count):
        s_print(char, end=False)
    s_print("")


class BusStat(Stat):
    def __init__(self, internal_stat=None, movement_type=serving, init_movements=None):
        super(BusStat, self).__init__(internal_stat, movement_type)
        if init_movements is None:
            init_movements = {}
        self.movements = {}
        self.movements = dict_add(self.movements, init_movements)

    def add_stat(self, stat, movement_type=serving):
        super(BusStat, self).add_stat(stat, movement_type)
        self.movements = dict_add(self.movements, stat.movements)

    def print(self, info=""):
        print_hf(stat_header_length, info=info)
        super(BusStat, self).print()
        print_hf(movements_header_length, info="BUS MOVEMENTS")
        for time_in_seconds in sorted(self.movements.keys()):
            s_movement = self.movements[time_in_seconds]
            for movement in s_movement:
                s_print(movement.__str__())


class TotalStat(Stat):
    def __init__(self, internal_stat=None):
        super(TotalStat, self).__init__(internal_stat)

    def print(self, info=""):
        print_hf(stat_header_length, info="TOTAL")
        super(TotalStat, self).print()
        print_hf(stat_footer_length)
