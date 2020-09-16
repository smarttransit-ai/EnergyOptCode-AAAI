import numpy as np

from base.entity.Location import ChargingPoint
from base.entity.Route import Route
from base.util.common_util import fetch_stops
from common.Time import add, time, t_less_or_eq, t_less_than
from common.configs.global_constants import cp_locations, default_slot_duration, key_end
from common.configs.model_constants import gas_bus_type


class TimeSlot(object):
    def __init__(self, start, _diff):
        self.start = start
        self.diff = _diff
        self.finish = add(start, _diff)

    def diff_hours(self):
        return self.diff.time_in_seconds / 3600

    def __key__(self):
        return self.start.__key__() + "_" + self.finish.__key__()


class Charging(object):
    def __init__(self, pole, slot, charging_id):
        self.pole = pole
        self.slot = slot
        # these are bad fixes still used to reduce unwanted if clauses
        self.route = Route(pole, pole)
        self.start_time = slot.start
        self.end_time = slot.finish
        self.charging_id = charging_id

    def get_duration(self):
        return self.slot.diff

    def start_in_slot(self, slot):
        return is_trip_in_slot(slot, self)

    @staticmethod
    def get_energy_cost(bus_type):
        if bus_type.type_name == gas_bus_type.type_name:
            raise TypeError("Gas vehicles can't be charged")
        else:
            return 0

    def __str__(self):
        return "CHR_TRIP | " + self.pole.__str__()

    def __key__(self):
        return "C" + str(self.charging_id) + key_end

    def __content__(self):
        return self.__key__() + "," + self.pole.__str__() + "," + \
               self.start_time.time + "," + self.end_time.time + ","


def create_poles():
    poles = []
    stops = fetch_stops()
    for stop_id in sorted(stops.keys()):
        if stop_id in cp_locations:
            current_stop = stops[stop_id]
            poles.append(ChargingPoint(current_stop))
    return poles


def create_slots(slot_duration=default_slot_duration):
    time_slots = []
    for i in np.arange(0, 24, slot_duration):
        time_slots.append(TimeSlot(time(i * 3600), time(3600 * slot_duration)))
    return time_slots


def create_charging(slot_duration=default_slot_duration):
    poles = create_poles()
    slots = create_slots(slot_duration)
    _charging = []
    charging_id = 0
    for pole in poles:
        for slot in slots:
            s_charging = Charging(pole, slot, charging_id)
            _charging.append(s_charging)
            charging_id += 1
    return _charging


def is_trip_in_slot(slot, trip):
    in_slot = False
    if t_less_or_eq(slot.start, trip.start_time) and t_less_than(trip.start_time, slot.finish):
        in_slot = True
    return in_slot


def is_mov_trip_in_slot(slot, prev_trip):
    in_slot = False
    if t_less_or_eq(slot.start, prev_trip.end_time) and t_less_than(prev_trip.end_time, slot.finish):
        in_slot = True
    return in_slot
