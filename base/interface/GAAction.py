import random as rand

from base.interface.SwapInterface import SwapInterface
from common.Time import time, t_less_than


class GAAction(SwapInterface):
    def __init__(self):
        self._e_start_time = time(24 * 60 * 60)
        self._l_start_time = time(0)

    def reset(self):
        self._e_start_time = time(24 * 60 * 60)
        self._l_start_time = time(0)

    def crossover_init(self):
        cross_over_initial = self.base_copy()
        cross_over_remaining = self.base_copy()
        times = [trip.start_time for trip in self.get_trips()]
        times = sorted(times, key=lambda _time: _time.time_in_seconds)
        cross_over_start_time = times[int(len(times) / 2)]
        for selected_trip in self.get_trips():
            selected_bus = self.get(selected_trip)
            if t_less_than(selected_trip.start_time, cross_over_start_time):
                cross_over_initial.assign(selected_trip, selected_bus)
            else:
                cross_over_remaining.assign(selected_trip, selected_bus)
        return cross_over_initial, cross_over_remaining

    def mutate(self):
        swapped = False
        child = self.copy()
        buses_list = child.get_buses()
        if len(buses_list) > 2:
            selected_bus_a = rand.choice(buses_list)
            selected_bus_b = rand.choice(buses_list)
            child, swapped = self._mutate(child, selected_bus_a, selected_bus_b)
        return child, swapped

    def _mutate(self, child, selected_bus_a, selected_bus_b):
        return self._inner_swap(child, selected_bus_a, selected_bus_b)

    def base_copy(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def get_trips(self):
        raise NotImplementedError

    def add(self, key, val):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError
