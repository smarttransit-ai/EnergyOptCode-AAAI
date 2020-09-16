import math

from base.entity.Charging import is_trip_in_slot
from base.entity.EnergyConsumed import energy_consumed
from base.entity.Route import Route
from common.Time import add
from common.configs.model_constants import electric_bus_type, gas_bus_type


class Trip(object):
    def __init__(self, start_pos, end_pos):
        self.route = Route(start_pos, end_pos)
        self.energy_consumed = math.inf
        self.energy_cost = math.inf
        self.start_time = None
        self.end_time = None
        self.trip_id = ""

    def add_locations(self, locations):
        self.route.add_locations(locations)

    def add_duration(self, duration_est):
        self.route.add_duration_est(duration_est)
        self.end_time = add(self.start_time, self.route.duration_est)

    def set_distance(self, _distance):
        self.route.distance = _distance

    def add_soc(self, _soc):
        self.route.soc = _soc

    def add_gasoline_energy(self, _gasoline):
        self.route.gasoline = _gasoline

    def get_locations(self):
        return self.route.locations

    def get_stops(self):
        return self.route.stops

    def set_start_time(self, start_time):
        self.start_time = start_time
        self.end_time = add(self.start_time, self.route.duration_est)

    def get_duration(self):
        return self.route.duration_est

    def get_end_time(self):
        return self.end_time

    def get_energy_consumed(self, bus_type):
        self.energy_consumed = energy_consumed(self.route, bus_type).energy
        return self.energy_consumed

    def get_energy_cost(self, bus_type):
        self.energy_cost = energy_consumed(self.route, bus_type).cost
        return self.energy_cost

    def start_in_slot(self, slot):
        return is_trip_in_slot(slot, self)

    def __str__(self):
        raise NotImplementedError

    def __key__(self):
        raise NotImplementedError

    def __content__(self):
        return self.__key__() + "," + self.__str__() + "," + \
               self.start_time.time + "," + self.get_end_time().time + "," + \
               str(energy_consumed(self.route, electric_bus_type).energy) + "," + \
               str(energy_consumed(self.route, gas_bus_type).energy) + ","
