# -------------------------------------------------------------------------------- #
#                 GENERATE DUMP STRUCTURE FOR INTEGER PROGRAMMING                  #
# -------------------------------------------------------------------------------- #
from collections import namedtuple

from base.dump.DumpIPGenAssist import DumpIPGenAssist
from base.entity.Charging import Charging, create_slots, is_mov_trip_in_slot
from base.entity.EnergyConsumed import electric_energy
from base.entity.MovingTrip import movable, get_mov_energy
from base.entity.OperatingTrip import OperatingTrip
from common.configs.model_constants import electric_bus_type

GlobalMiniTempStore = namedtuple('GlobalMiniTempStore', ['assign_temp_store', 'move_temp_store', 'charge_temp_store'])
AssignMiniTempStore = namedtuple('AssignMiniTempStore', ['assign_key_list', 'assign_energies'])
MoveMiniTempStore = namedtuple('MoveMiniTempStore', ['move_key_list', 'move_energies'])
ChargeMiniTempStore = namedtuple('ChargeMiniTempStore', ['charge_key_list', 'charge_energies'])


class DumpIPGenAssistWTC(DumpIPGenAssist):
    def compute_bus_slot_filtered_data(self, dump_config, dump_structure):
        slots = create_slots(dump_config.slot_duration)
        all_trips = self.get_all_trips(dump_structure)
        assign_temp_store, charge_temp_store = self.compute_assign_in_filtered_data_by_bus(all_trips, slots)
        mov_temp_store = self.compute_move_in_filtered_data_by_bus(dump_structure, slots)
        glb_temp_store = GlobalMiniTempStore(assign_temp_store, mov_temp_store, charge_temp_store)
        return glb_temp_store

    def compute_assign_in_filtered_data_by_bus(self, all_trips, slots):
        assign_key_list = {}
        charge_key_list = {}
        assign_energies = {}
        charge_energies = {}
        for slot in slots:
            slot_key = self.combine_key([slot])

            if slot_key not in assign_key_list.keys():
                assign_key_list[slot_key] = []
            if slot_key not in assign_energies.keys():
                assign_energies[slot_key] = {}

            if slot_key not in charge_key_list.keys():
                charge_key_list[slot_key] = []
            if slot_key not in charge_energies.keys():
                charge_energies[slot_key] = {}

        for trip in all_trips:
            key = self.combine_key([trip])
            for slot in slots:
                if trip.start_in_slot(slot):
                    slot_key = self.combine_key([slot])

                    if isinstance(trip, OperatingTrip):
                        assign_key_list[slot_key].append(key)
                        assign_energies[slot_key][key] = electric_energy(trip)

                    elif isinstance(trip, Charging):
                        charge_key_list[slot_key].append(key)
                        charge_energies[slot_key][key] = slot.diff_hours() * trip.pole.performance

        assign_temp_store = AssignMiniTempStore(assign_key_list, assign_energies)
        charge_temp_store = ChargeMiniTempStore(charge_key_list, charge_energies)
        return assign_temp_store, charge_temp_store

    def compute_move_in_filtered_data_by_bus(self, dump_structure, slots):
        all_trips = self.get_all_trips(dump_structure)
        move_key_list = {}
        move_energies = {}
        for slot in slots:
            slot_key = self.combine_key([slot])
            if slot_key not in move_key_list.keys():
                move_key_list[slot_key] = []
            if slot_key not in move_energies.keys():
                move_energies[slot_key] = {}
        for slot in slots:
            s_slot_key = self.combine_key([slot])
            all_trips = sorted(all_trips, key=lambda _trip: _trip.start_time.time_in_seconds)
            for trip_1 in all_trips:
                if is_mov_trip_in_slot(slot, trip_1):
                    all_trips = sorted(all_trips, key=lambda _trip: _trip.start_time.time_in_seconds)
                    for trip_2 in all_trips:
                        i = all_trips.index(trip_1)
                        j = all_trips.index(trip_2)
                        if j > i:
                            key = self.combine_key([trip_1, trip_2])
                            if movable(trip_1, trip_2):
                                move_key_list[s_slot_key].append(key)
                                energy = get_mov_energy(trip_1, trip_2, electric_bus_type)
                                move_energies[s_slot_key][key] = energy
        mov_temp_store = MoveMiniTempStore(move_key_list, move_energies)
        return mov_temp_store
