# -------------------------------------------------------------------------------- #
#                 FETCHING INITIAL DATA AND OTHER BASIC UTILITIES                  #
# -------------------------------------------------------------------------------- #
from base.entity.GTFSEntities import Shape, BusTrip, Stop, StopTime
from common.configs.global_constants import mile_to_meter, input_dump_directory, input_data_directory
from common.util import pickle_util as custom_pickle


def fetch_shapes():
    import pandas as pd
    shapes_dump_file = input_dump_directory + "shapes.dat"
    shape_dict = {}
    try:
        shape_dict = custom_pickle.load_obj(shapes_dump_file)
    except FileNotFoundError:
        for shape_data in pd.read_csv(input_data_directory + "shapes.txt", chunksize=1):
            shape = Shape(shape_data)
            key_sh = shape.__dict__["shape_id"]
            if key_sh in shape_dict.keys():
                shape_dict[key_sh].append(shape)
            else:
                shape_dict[key_sh] = [shape]
        custom_pickle.dump_obj(shape_dict, shapes_dump_file)
    return shape_dict


def fetch_trips():
    import pandas as pd
    trips_dump_file = input_dump_directory + "trips.dat"
    trips = []
    try:
        trips = custom_pickle.load_obj(trips_dump_file)
    except FileNotFoundError:
        for trip_data in pd.read_csv(input_data_directory + "trips.txt", chunksize=1):
            trip = BusTrip(trip_data)
            trips.append(trip)
        custom_pickle.dump_obj(trips, trips_dump_file)
    return trips


def fetch_stop_times():
    import pandas as pd
    stop_times_dump_file = input_dump_directory + "stop_times.dat"
    trip_stop_times_dict = {}
    try:
        trip_stop_times_dict = custom_pickle.load_obj(stop_times_dump_file)
    except FileNotFoundError:
        for stop_time_data in pd.read_csv(input_data_directory + "stop_times.txt", chunksize=1):
            stop_time = StopTime(stop_time_data)
            key = stop_time.__dict__["trip_id"]
            if key in trip_stop_times_dict.keys():
                trip_stop_times_dict[key].append(stop_time)
            else:
                trip_stop_times_dict[key] = [stop_time]
        custom_pickle.dump_obj(trip_stop_times_dict, stop_times_dump_file)
    return trip_stop_times_dict


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
