import random as rand
from enum import Enum

from base.interface.SwapInterface import SwapInterface


class Strategy(Enum):
    SARandom = 0


def get_buses_by_strategy(assign, strategy):
    buses = []
    if strategy == Strategy.SARandom:
        buses = assign.get_buses()
    return buses


class SAActionBase(SwapInterface):
    def __init__(self, strategy):
        self.strategy = strategy

    def swap(self):
        swapped = False
        child = self.copy()
        buses_list = get_buses_by_strategy(child, self.strategy)
        if len(buses_list) > 2:
            selected_bus_a, selected_bus_b = self._choose_buses(buses_list)
            child, swapped = self._inner_swap(child, selected_bus_a, selected_bus_b)
        return child, swapped

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

    def _choose_buses(self, buses_list):
        raise NotImplementedError


class SAAction(SAActionBase):
    def __init__(self):
        super(SAAction, self).__init__(Strategy.SARandom)

    def _choose_buses(self, buses_list):
        selected_bus_a = rand.choice(buses_list)
        selected_bus_b = rand.choice(buses_list)
        return selected_bus_a, selected_bus_b

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
