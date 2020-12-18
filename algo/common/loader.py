import os

from base.util.trips_util import clean_dumps, create_dumps, move_trips_mini_dump_file
from common.util import pickle_util as custom_pickle


def load_moving_trips():
    """
    Returns:
        dictionary of moving trips details
    """
    if not os.path.exists(move_trips_mini_dump_file):
        clean_dumps()
        create_dumps()

    _mov_trips = custom_pickle.load_obj(move_trips_mini_dump_file)

    return _mov_trips


mov_trips = load_moving_trips()
