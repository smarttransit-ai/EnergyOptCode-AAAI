# -------------------------------------------------------------------------------- #
#                    GENERATE BASIC MODEL STRUCTURE FOR TRIPS                      #
# -------------------------------------------------------------------------------- #
from base.entity.OperatingTrip import OperatingTrip
from base.util.common_util import fetch_shapes, fetch_trips, fetch_stops, fetch_stop_times, get_euclidean_distance
from common.configs.global_constants import data_week_directory, day_code, agency_mode
from common.mode.ServiceMode import get_time_stamp, get_range_values
from common.util import pickle_util as custom_pickle
from common.util.common_util import s_print_err, s_print_warn, create_dir

gtfs_dump_file = data_week_directory + "gtfs_dump.dat"
gtfs_mini_dump_file = data_week_directory + "gtfs_mini_dump.dat"

trips_csv_file = data_week_directory + "trips.csv"

mov_trips_csv_file = data_week_directory + "move_trips.csv"
move_trips_dump_file = data_week_directory + "move_trips_dump.dat"
move_trips_mini_dump_file = data_week_directory + "move_trips_mini_dump.dat"

se_dump_file = data_week_directory + "se_dump.dat"
json_dump_file = data_week_directory + "json_dump.dat"

trip_count_csv_file = data_week_directory + "trip_counts.csv"


class StopTimeEx(object):
    def __init__(self, stop, stop_time):
        self.stop = stop
        self.stop_time = stop_time


def delete_file(file):
    """
    Args:
        file: name of the file with full path which will be deleted
        if there exist a file matching the name of the file, this
        function will delete the file
    """
    import os
    if os.path.exists(file):
        os.remove(file)


def clean_dumps():
    """
    This will clean all the random_samples to start fresh
    """
    dump_names = ["gtfs", "gtfs_mini", "json", "move_trips", "move_trips_mini", "se"]
    for dump_name in dump_names:
        delete_file(data_week_directory + dump_name + "_dump.dat")


def create_dumps():
    """
    This will create the random_samples to load the data easily
    """
    extract_trips()
    extract_trips_minimal()
    extract_moving_trips()
    extract_moving_trip_minimal()


def merge_files(file_name):
    """
    This function  is used to merge the file contents and write to
    a single file with the given file_name

    Note : it is assumed the files to be merged follow the same pattern
    of the file_name
    """
    import os
    contents = []
    i = 0
    while True:
        sub_file_path = file_name.replace(".csv", f"/{i}.csv")
        if os.path.exists(sub_file_path):
            sub_file = open(sub_file_path, "r+")
            contents.extend(sub_file.readlines())
            sub_file.close()
            i += 1
        else:
            break
    if len(contents) > 0:
        merge_file = open(file_name, "w+")
        merge_file.writelines(contents)
        merge_file.close()


def split_files(file_name, lines_limit=500000):
    """
    Args:
        file_name: name of the file, probably the file_name for energy estimates
        lines_limit: number of lines for each smaller files generated from the large file
    """
    import pandas as pd
    dir_name = file_name.replace(".csv", "")
    df = pd.read_csv(file_name, usecols=["Start_Lat", "Start_Lon",
                                         "End_Lat", "End_Lon", "Path_Timestamp",
                                         "Predicted_Values"], index_col=False)
    df.to_csv(file_name, columns=["Start_Lat", "Start_Lon", "End_Lat", "End_Lon", "Path_Timestamp",
                                  "Predicted_Values"], index=False)
    input_file = open(file_name, "r+")
    contents = input_file.readlines()
    number_of_sub_portion = int(len(contents) / lines_limit)
    create_dir(dir_name)
    for i in range(number_of_sub_portion + 2):
        out_file = open(dir_name + "/{0}.csv".format(str(i)), "w+")
        out_file.writelines(contents[i * lines_limit:(i + 1) * lines_limit])
        out_file.close()
    input_file.close()


def get_energy_values(file_name):
    """
    Args:
        file_name: name of the file containing energy estimates
    Returns:
        dictionary of energy estimates
    """
    import os
    import pandas as pd
    line_count = 0
    time_stamp_day_code = get_time_stamp(day_code)
    energy_consumptions = {}
    file_name = data_week_directory + file_name
    try:
        if not os.path.exists(file_name):
            merge_files(file_name)
        df = pd.read_csv(file_name, usecols=["Start_Lat", "Start_Lon",
                                             "End_Lat", "End_Lon", "Path_Timestamp",
                                             "Predicted_Values"], index_col=False)
        df.to_csv(file_name, columns=["Start_Lat", "Start_Lon", "End_Lat", "End_Lon", "Path_Timestamp",
                                      "Predicted_Values"], index=False)
        _trips_csv_file = open(file_name, "r+")

        for line in _trips_csv_file.readlines()[1:]:
            line_count += 1
            start_lat, start_lon, end_lat, end_lon, timestamp, energy = line.split(",")
            key = round(float(start_lat), 5), round(float(start_lon), 5), \
                  round(float(end_lat), 5), round(float(end_lon), 5), \
                  int(timestamp) - time_stamp_day_code

            energy_value = 0
            if key in energy_consumptions.keys():
                energy_value = energy_consumptions[key]
            try:
                energy_value += float(energy)
            except ValueError:
                pass
            energy_consumptions[key] = energy_value
    except FileNotFoundError:
        s_print_err("{} file is missing !!!".format(file_name))
    return energy_consumptions.copy()


def extract_trips():
    """
    Returns:
        returns list of operating/service trips from GTFS dataset
    """
    try:
        operating_trips = custom_pickle.load_obj(gtfs_dump_file)
    except FileNotFoundError:
        shapes = fetch_shapes()
        trips = fetch_trips()
        stops = fetch_stops()
        trip_stop_times = fetch_stop_times()
        operating_trips = []
        for trip in trips:
            if trip.service_id == day_code.value:
                trip.set_shapes(shapes[trip.shape_id])
                stop_times = trip_stop_times[trip.trip_id]
                real_stops = []
                for stop_time in stop_times:
                    stop_id = stop_time.stop_id
                    stop = stops[stop_id]
                    real_stops.append(StopTimeEx(stop, stop_time))
                trip.set_start_and_end(real_stops[0], real_stops[-1])
                operating_trip = OperatingTrip(trip)
                if operating_trip.duration.time_in_seconds >= 180:
                    operating_trip.add_locations(trip.get_lat_lon())
                    operating_trip.add_stops(real_stops)
                    operating_trips.append(operating_trip)
        custom_pickle.dump_obj(operating_trips, gtfs_dump_file)
    return operating_trips


def extract_trips_minimal():
    """
    Returns:
        returns minimal version of operating trips,
        this will reduce the memory usage in dump generation especially in IP
    """
    try:
        operating_trips = custom_pickle.load_obj(gtfs_mini_dump_file)
    except FileNotFoundError:
        shapes = fetch_shapes()
        trips = fetch_trips()
        stops = fetch_stops()
        trip_stop_times = fetch_stop_times()
        electric_energy_consumptions = get_energy_values("Trips_electric_predict.csv")
        gasoline_energy_consumptions = get_energy_values("Trips_gas_predict.csv")
        missing_trip_energies = open(data_week_directory + "trips.csv.missing", "w+")
        operating_trips = []
        bus_line_trip_counts = {}
        bus_line_min_trip_time = {}
        missing_write_once = False
        for trip in trips:
            if trip.service_id == day_code.value:
                if trip.route_id in bus_line_trip_counts.keys():
                    bus_line_trip_counts[trip.route_id] += 1
                else:
                    bus_line_trip_counts[trip.route_id] = 1
                trip.set_shapes(shapes[trip.shape_id])
                stop_times = trip_stop_times[trip.trip_id]
                real_stops = []
                for stop_time in stop_times:
                    stop_id = stop_time.stop_id
                    stop = stops[stop_id]
                    real_stops.append(StopTimeEx(stop, stop_time))
                trip.set_start_and_end(real_stops[0], real_stops[-1])
                energy_key = trip.trip_key()
                operating_trip = OperatingTrip(trip)
                if operating_trip.duration.time_in_seconds > 200:
                    if trip.route_id in bus_line_min_trip_time.keys():
                        min_duration = bus_line_min_trip_time[trip.route_id]
                        if operating_trip.duration.time_in_seconds < min_duration:
                            bus_line_min_trip_time[trip.route_id] = operating_trip.duration.time_in_seconds
                    else:
                        bus_line_min_trip_time[trip.route_id] = operating_trip.duration.time_in_seconds
                    missing = False
                    if energy_key in electric_energy_consumptions.keys():
                        electric_value = electric_energy_consumptions[energy_key]
                        operating_trip.add_soc(electric_value)
                    else:
                        missing = True
                    if energy_key in gasoline_energy_consumptions.keys():
                        gasoline_value = gasoline_energy_consumptions[energy_key]
                        operating_trip.add_gasoline_energy(gasoline_value)
                    else:
                        missing = True
                    if missing:
                        missing_trip_energies.write(str(energy_key) + "\n")
                        missing_write_once = True
                    operating_trip.set_distance(get_euclidean_distance(trip.get_lat_lon()))
                    operating_trips.append(operating_trip)
        custom_pickle.dump_obj(operating_trips, gtfs_mini_dump_file)
        trip_count_file = open(trip_count_csv_file, "w+")
        trip_count_file.write("route_id,number_of_trips,min_duration\n")
        for route_id in bus_line_trip_counts.keys():
            min_trip_time = 0
            if route_id in bus_line_min_trip_time:
                min_trip_time = bus_line_min_trip_time[route_id]
            write_line = "{},{},{}\n".format(route_id, bus_line_trip_counts[route_id], str(min_trip_time))
            trip_count_file.write(write_line)
        trip_count_file.close()
        missing_trip_energies.close()
        if not missing_write_once:
            delete_file(data_week_directory + "trips.csv.missing")
    return operating_trips


def merge_json_dump():
    """
        This function merge all the JSON responses collected from
        Direction API into a single file.
    """
    import zipfile
    import shutil
    import os
    full_json_responses = {}

    _data_week_directory = data_week_directory
    if agency_mode == "DATA_2019":
        suffices_2019 = ["5_11", "11_17", "17_23"]
        for suffix in suffices_2019:
            _json_dump_file = data_week_directory + "json_dumps/json_dump_n_" + suffix + "_1.dat"
            try:
                json_responses = custom_pickle.load_obj(_json_dump_file)
                full_json_responses.update(json_responses.copy())
            except FileNotFoundError:
                s_print_err(_json_dump_file + " is missing !!!")
        for suffix in suffices_2019:
            _json_dump_file = data_week_directory + "json_dumps/json_dump_n_" + suffix + "_2.dat"
            try:
                json_responses = custom_pickle.load_obj(_json_dump_file)
                full_json_responses.update(json_responses.copy())
            except FileNotFoundError:
                s_print_err(_json_dump_file + " is missing !!!")

    _json_dump_file = data_week_directory + "json_dump.dat"
    custom_pickle.dump_obj(full_json_responses, _json_dump_file)


def start_end_dump_generation():
    """
    Returns:
        returns list of start and end points for route which can be used
        to compute the moving trips
    """
    start_end_points = {}
    routes = {}
    try:
        start_end_points, routes = custom_pickle.load_obj(se_dump_file)
    except FileNotFoundError:
        trips = extract_trips_minimal()
        for trip in trips:
            start_lat_lon = trip.route.start_pos.lat_lon()
            end_lat_lon = trip.route.end_pos.lat_lon()
            if (start_lat_lon, end_lat_lon) not in routes.keys():
                routes[(start_lat_lon, end_lat_lon)] = trip
                if start_lat_lon not in start_end_points.keys():
                    start_end_points[start_lat_lon] = trip.route.start_pos
                if end_lat_lon not in start_end_points.keys():
                    start_end_points[end_lat_lon] = trip.route.end_pos
        custom_pickle.dump_obj((start_end_points, routes), se_dump_file)
    return start_end_points, routes


def json_response_dump_generation():
    """
    Returns:
        this will returns the dictionary of json dump.
        this function was kept as in same flow. but no longer used.
    """
    json_responses = {}
    try:
        json_responses = custom_pickle.load_obj(json_dump_file)
    except FileNotFoundError:
        '''
            Functionality to handle this exception can be found in the 
            ```fetch``` directory
        '''
        s_print_err(json_dump_file + " file is missing !!!")
    return json_responses


def extract_moving_trips():
    """
    Returns:
        returns dictionary basic moving trip details
    """
    import itertools
    start_end_points, routes = start_end_dump_generation()
    merge_json_dump()
    json_responses = json_response_dump_generation()
    __mov_trips = {}
    try:
        __mov_trips = custom_pickle.load_obj(move_trips_dump_file)
    except FileNotFoundError:
        time_stamp_day_code = get_time_stamp(day_code)
        start, end = get_range_values(agency_mode, day_code)
        time_stamp_diff = 3600
        time_stamps = [time_stamp_day_code + time_stamp_diff * i for i in range(start, end)]
        trip_id = 0
        missing_trip_energies = open(data_week_directory + "mov_trips_json.csv.missing", "w+")
        missing_write_once = False
        for i, time_stamp in enumerate(time_stamps):
            for (lat_lon_i, lat_lon_j) in itertools.product(start_end_points.keys(), start_end_points.keys()):
                if lat_lon_i != lat_lon_j:
                    key = (lat_lon_i, lat_lon_j, time_stamp)
                    if key in json_responses.keys():
                        parsed_json = json_responses[key]
                        gtfs_routes = parsed_json["routes"]
                        if len(gtfs_routes) > 0:
                            trip_id += 1
                            route = gtfs_routes[0]
                            legs = route["legs"]
                            if len(legs) > 1:
                                s_print_warn("Number of legs : {}".format(str(len(legs))))
                            leg = legs[0]
                            _distance = leg["distance"]["value"]
                            _duration = leg["duration"]["value"]
                            __mov_trips[(lat_lon_i, lat_lon_j, time_stamp - time_stamp_day_code)] = \
                                (_duration, _distance, trip_id)
                    else:
                        missing_write_once = True
                        missing_trip_energies.write(str((lat_lon_i, lat_lon_j, time_stamp)) + "\n")
                else:
                    trip_id += 1
                    __mov_trips[(lat_lon_i, lat_lon_j, time_stamp - time_stamp_day_code)] = \
                        (0, 0, trip_id)
        custom_pickle.dump_obj(__mov_trips, move_trips_dump_file)
        missing_trip_energies.close()
        if not missing_write_once:
            delete_file(data_week_directory + "mov_trips_json.csv.missing")
    return __mov_trips


def extract_moving_trip_minimal():
    """
    Returns:
        returns dictionary basic moving trip details
    """
    __moving_trips = {}
    try:
        __moving_trips = custom_pickle.load_obj(move_trips_mini_dump_file)
    except FileNotFoundError:
        electric_energy_consumptions = get_energy_values("MTrips_electric_predict.csv")
        gasoline_energy_consumptions = get_energy_values("MTrips_gas_predict.csv")

        missing_trip_energies = open(data_week_directory + "mov_trips.csv.missing", "w+")
        missing_write_once = False
        mov_trips = extract_moving_trips()
        for mov_trip_key in mov_trips.keys():
            lat_lon_i, lat_lon_j, time_in_sec = mov_trip_key
            (_duration, _distance, _trip_id) = mov_trips[mov_trip_key]
            lat_i, lon_i = lat_lon_i.split(",")
            lat_j, lon_j = lat_lon_j.split(",")
            energy_key = round(float(lat_i), 5), round(float(lon_i), 5), \
                         round(float(lat_j), 5), round(float(lon_j), 5), time_in_sec
            electric = 0
            missing = False
            if lat_lon_i != lat_lon_j:
                if energy_key in electric_energy_consumptions.keys():
                    electric = electric_energy_consumptions[energy_key]
                else:
                    missing = True
            gasoline = 0
            if lat_lon_i != lat_lon_j:
                if energy_key in gasoline_energy_consumptions.keys():
                    gasoline = gasoline_energy_consumptions[energy_key]
                else:
                    missing = True
            if missing:
                missing_trip_energies.write(str(energy_key) + "\n")
                missing_write_once = True
            __moving_trips[mov_trip_key] = (_duration, _distance, electric, gasoline, _trip_id)
        custom_pickle.dump_obj(__moving_trips, move_trips_mini_dump_file)
        missing_trip_energies.close()
        if not missing_write_once:
            delete_file(data_week_directory + "mov_trips.csv.missing")
    return __moving_trips
