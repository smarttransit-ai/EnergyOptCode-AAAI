from base.entity.EnergyConsumed import energy_consumed
from base.util.common_util import get_euclidean_distance
from common.Time import time


class Route(object):
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.route_id = None
        self.distance = 0
        self.soc = 0
        self.gasoline = 0
        self.locations = []
        self.stops = []
        self.duration_est = time(0)

    def add_route_id(self, route_id):
        self.route_id = route_id

    def add_locations(self, locations):
        self.locations = locations
        self.set_euclidean_distance()

    def add_duration_est(self, duration_est):
        self.duration_est = time(duration_est)

    def add_stops(self, stops):
        self.stops = stops

    def energy_consumed(self, vehicle_type):
        return energy_consumed(self, vehicle_type)

    def set_euclidean_distance(self):
        self.distance = get_euclidean_distance(self.locations)

    def __str__(self):
        format_string = self.start_pos.location_name + " => " + self.end_pos.location_name
        return format_string.replace("\"", "\'")

    def __key__(self):
        key_string = self.start_pos.location_name + "_" + self.end_pos.location_name
        return key_string.replace("\"", "")
