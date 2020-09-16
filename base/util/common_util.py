# -------------------------------------------------------------------------------- #
#                 FETCHING INITIAL DATA AND OTHER BASIC UTILITIES                  #
# -------------------------------------------------------------------------------- #
from base.entity.GTFSEntities import Stop
from common.configs.global_constants import mile_to_meter, input_dump_directory, input_data_directory
from common.util import pickle_util as custom_pickle


def fetch_stops():
    import pandas as pd
    stops_dump_file = input_dump_directory + "stops.dat"
    stops = {}
    try:
        stops = custom_pickle.load_obj(stops_dump_file)
    except FileNotFoundError:
        for stop_data in pd.read_csv(input_data_directory + "stops.txt", chunksize=1):
            stop = Stop(stop_data)
            key = stop.__dict__["stop_id"]
            stops[key] = stop
        custom_pickle.dump_obj(stops, stops_dump_file)
    return stops


def get_euclidean_distance(route_locations):
    from geopy.distance import distance
    total_distance = 0
    for i, start in enumerate(route_locations[:-1]):
        end = route_locations[i + 1]
        total_distance += distance(start, end).miles
    return total_distance * mile_to_meter
