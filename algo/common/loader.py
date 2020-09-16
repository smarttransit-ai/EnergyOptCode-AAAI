from common.configs.global_constants import data_week_directory
from common.util import pickle_util as custom_pickle

move_trips_mini_dump_file = data_week_directory + "move_trips_mini_dump.dat"


def load_moving_trips():
    """
    Returns:
        dictionary of moving trips details
    """
    _mov_trips = custom_pickle.load_obj(move_trips_mini_dump_file)
    return _mov_trips


mov_trips = load_moving_trips()
