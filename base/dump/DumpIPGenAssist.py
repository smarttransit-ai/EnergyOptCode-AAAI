# -------------------------------------------------------------------------------- #
#                 GENERATE DUMP STRUCTURE FOR INTEGER PROGRAMMING                  #
# -------------------------------------------------------------------------------- #
from collections import namedtuple

from base.entity.MovingTrip import movable
from common.configs.global_constants import dump_directory
from common.configs.model_constants import electric_bus_type
from common.util import pickle_util as custom_pickle


def get_key(item):
    _key = ""
    if type(item) == str:
        _key = item
    else:
        _key = "_" + item.__key__() + "_"
    return _key


def combine_key(items):
    if len(items) == 0:
        return items
    combine_key_str = get_key(items[0])
    for item in items[1:]:
        combine_key_str += get_key(item)
    return combine_key_str


def is_contain_in_combined(_combined_key, items):
    for item in items:
        if item.__key__() not in _combined_key:
            return False
    return True


MoveNonMoveTempStore = namedtuple('MoveNonMoveTempStore', ['move_trips_pairs', 'n_move_trips_pairs'])


class DumpIPGenAssist(object):
    @staticmethod
    def get_all_trips(dump_structure, _bus_type=None):
        all_trips = dump_structure.filtered_trips.copy()
        if _bus_type is not None and _bus_type.type_name == electric_bus_type.type_name:
            all_trips.extend(dump_structure.charging.copy())
        elif _bus_type is None and "charging" in dump_structure.__dict__.keys():
            all_trips.extend(dump_structure.charging.copy())
        return sorted(all_trips, key=lambda trip: trip.start_time.time_in_seconds)

    @staticmethod
    def combine_key(items):
        return combine_key(items)

    @staticmethod
    def is_contain_in_combined(_combined_key, items):
        return is_contain_in_combined(_combined_key, items)

    def compute_filtered_data(self, dump_config, dump_structure):
        all_trips = self.get_all_trips(dump_structure)
        moving_dump_file_name = dump_directory + dump_config.__key__() + "_move_trips.dat"
        try:
            mv_n_mv_temp_store = custom_pickle.load_obj(moving_dump_file_name)
        except FileNotFoundError:
            move_trips_pairs = []
            non_move_trips_pairs = []
            all_trips = sorted(all_trips, key=lambda _trip: _trip.start_time.time_in_seconds)
            for trip_1 in all_trips:
                all_trips = sorted(all_trips, key=lambda _trip: _trip.start_time.time_in_seconds)
                for trip_2 in all_trips:
                    i = all_trips.index(trip_1)
                    j = all_trips.index(trip_2)
                    if j > i:
                        if movable(trip_1, trip_2):
                            move_trips_pairs.append((trip_1, trip_2))
                        else:
                            non_move_trips_pairs.append((trip_1, trip_2))
            mv_n_mv_temp_store = MoveNonMoveTempStore(move_trips_pairs, non_move_trips_pairs)
            custom_pickle.dump_obj(mv_n_mv_temp_store, moving_dump_file_name)
        return mv_n_mv_temp_store
