# -------------------------------------------------------------------------------- #
#                      GENERATE RANDOM DUMP DATA AND LOADING                       #
# -------------------------------------------------------------------------------- #

import os
import random
from datetime import datetime

from base.dump.DumpIPGenAssist import DumpIPGenAssist
from base.dump.DumpStructure import DumpStructure, DumpStructureIP
from base.entity.Bus import create_buses
from base.util.trips_util import extract_trips_minimal, trip_count_csv_file
from common.Time import diff, time
from common.configs.global_constants import macosx_directory, dump_directory, \
    dump_log_directory, dump_info_directory, selected_date, rw_mode, default_time_tol, trips_directory, random_seed
from common.constants import convert_month_day_num_to_str
from common.util import pickle_util as custom_pickle
from common.util.common_util import create_dir, delete_dir, s_print_err
from common.writer.FileAppender import FileAppender
from common.writer.FileWriter import FileWriter


def read_bus_line_trip_info(dump_config, file_name):
    """
    Args:
        dump_config: Configuration of the dump
        file_name: trip_counts.csv, provide the exact file either GTFS based
                   or real-world data based
    Returns:
        the available routes satisfying the conditions
    """
    import pandas as pd
    df_selected = pd.read_csv(file_name)
    if dump_config.route_limit <= 6:
        df_trip_filter = df_selected[df_selected["number_of_trips"] >= dump_config.trip_limit]
        df_min_upper = df_trip_filter[df_trip_filter["min_duration"] >= 1500]
        df_min_lower = df_min_upper[df_min_upper["min_duration"] <= 1800]
        df_selected = df_min_lower
    elif dump_config.route_limit <= 12:
        df_trip_filter = df_selected[df_selected["number_of_trips"] >= dump_config.trip_limit]
        df_min_upper = df_trip_filter[df_trip_filter["min_duration"] >= 840]
        df_min_lower = df_min_upper[df_min_upper["min_duration"] <= 2400]
        df_selected = df_min_lower
    available_routes = df_selected["route_id"]
    available_routes = available_routes.to_list()
    if len(available_routes) < dump_config.route_limit:
        s_print_err("Insufficient routes, please reduce the trip limits per bus line")
        exit()
    return available_routes


def extract_specific_data_random(dump_config, operating_trips=None):
    """
    Args:
        dump_config: configuration of the dump
        operating_trips: available operating trips
    Returns:
        selected operating trips and their corresponding bus line numbers
    """
    _selected_trips = {}
    _route_values = []
    available_routes = read_bus_line_trip_info(dump_config, trip_count_csv_file)
    random.seed(random_seed)
    random.shuffle(operating_trips)
    return _extract_data(dump_config, operating_trips, available_routes)


def extract_specific_real_data_random(dump_config, operating_trips=None):
    """
    Args:
        dump_config: configuration of the dump
        operating_trips: available operating_trips
    Returns:
        selected operating trips and their corresponding bus line numbers
        unlike the extract_specific_data_random, here the data is based on real bus service
        in a particular day.
    """
    day = selected_date.day
    month = selected_date.month
    month_val, day_val = convert_month_day_num_to_str(str(month) + "/" + str(day))
    file_name = trips_directory + month_val + "/" + day_val + "/trip_counts.csv"
    available_routes = read_bus_line_trip_info(file_name, dump_config)
    random.seed(random_seed)
    random.shuffle(operating_trips)
    return _extract_data(dump_config, operating_trips, available_routes)


def _extract_data(dump_config, operating_trips, available_routes):
    _route_values = []
    _selected_trips = {}
    for trip in operating_trips:
        bus_line_no = trip.route.route_id
        # ignoring the shuttle services, consider the available routes
        if bus_line_no not in ["33", "34"] and bus_line_no in available_routes:
            if len(_route_values) < dump_config.route_limit:
                if bus_line_no in _selected_trips.keys():
                    _selected_trips[bus_line_no].append(trip)
                else:
                    _route_values.append(bus_line_no)
                    _selected_trips[bus_line_no] = [trip]
            elif len(_route_values) == dump_config.route_limit:
                if bus_line_no in _selected_trips.keys():
                    _selected_trips[bus_line_no].append(trip)
    return _selected_trips, _route_values


def generate_random_dump_data_internal(info_enabled=True, dump_config=None, operating_trips=None, suffix=""):
    """
    Args:
        info_enabled: this is a boolean value to determine updating info
        dump_config: dump configuration
        operating_trips: available operating trips
        suffix: additional suffix to contain multiple dump_structure with same dump_config
    Returns:
        selected operating trips
        Note : this function also update the dump.info file
    """
    if rw_mode:
        _selected_trips, _route_values = extract_specific_real_data_random(dump_config, operating_trips)
    else:
        _selected_trips, _route_values = extract_specific_data_random(dump_config, operating_trips)
    _filtered_trips = []
    if info_enabled:
        dump_info_file_name = dump_info_directory + dump_config.__key__() + suffix + "_dump.info"
        create_dir(dump_info_directory)
        route_details = FileWriter(dump_info_file_name)
        route_details.write("Total number of bus-lines : " + str(dump_config.route_limit))
        route_details.write("Maximum number of trips per bus-line : " + str(dump_config.trip_limit))
        route_details.write("\n[BUS LINE NUMBERS]\n" + "\n".join([str(route_no) for route_no in _route_values]))
        for route_no in _route_values:
            random.seed(random_seed)
            sample_trips = random.sample(_selected_trips[route_no],
                                         min(len(_selected_trips[route_no]), dump_config.trip_limit))
            route_details.write("\n[TRIPS FOR BUS LINE NUMBER : " + str(route_no) + "]")
            route_details.write("\nNo, Trip ID, Start Time, End Time, Duration")
            route_details_dict = {}
            for trip in sample_trips:
                _filtered_trips.append(trip)
                start_time_in_sec = trip.start_s()
                if start_time_in_sec in route_details_dict:
                    start_time_in_sec += random.randint(1, 100)
                route_details_dict[start_time_in_sec] = trip
            counter = 1
            for time_in_sec in sorted(route_details_dict.keys()):
                trip = route_details_dict[time_in_sec]
                route_details.write(", ".join([str(counter), str(trip.trip_id), str(trip.start_time.time),
                                               str(trip.end_time.time), str(trip.duration.time)]))
                counter += 1
        route_details.close()
    else:
        for route_no in _route_values:
            random.seed(random_seed)
            sample_trips = random.sample(_selected_trips[route_no],
                                         min(len(_selected_trips[route_no]), dump_config.trip_limit))
            for trip in sample_trips:
                _filtered_trips.append(trip)
    cleaned_trips = []
    for _trip in _filtered_trips:
        _duration = diff(_trip.end_time, _trip.start_time)
        _trip.end_time = diff(_trip.end_time, time(_duration.time_in_seconds * default_time_tol))
        _trip.duration = diff(_trip.end_time, _trip.start_time)
        cleaned_trips.append(_trip)
    return cleaned_trips


class DumpUtilBase(object):
    def __init__(self, is_serial=False, log_enabled=True, info_enabled=True):
        self.is_serial = is_serial
        self.log_enabled = log_enabled
        self.info_enabled = info_enabled
        self.dump_directory = ""
        self.dump_prefix = ""
        self.suffix = ""
        self.__setup()

    def __setup(self):
        self.dump_directory = dump_directory
        self.log_directory = dump_log_directory
        self.dump_prefix = "dump"

    def get_suffix(self):
        if self.suffix == "":
            suffix = "_"
        else:
            suffix = "_" + self.suffix + "_"
        return suffix

    def _make_dump_directory(self):
        create_dir(self.dump_directory)

    def update_dump_log(self, dump_config, start, end):
        if self.log_enabled:
            time_taken = end - start
            create_dir(self.log_directory)

            dump_log_file_name = self.log_directory + dump_config.__key__() + \
                                 self.get_suffix() + self.dump_prefix + ".log"
            file_writer = FileAppender(dump_log_file_name)
            file_writer.append("Dump generation started at " + str(start))
            file_writer.append("Dump generation finished at " + str(end))
            file_writer.append("Time taken for dump generation is " + str(time_taken))
            file_writer.close()

    def _load_filtered_data(self, dump_config):
        file_path = self.dump_directory + dump_config.__key__() + self.get_suffix() + self.dump_prefix + ".dat"
        self._make_dump_directory()
        if not os.path.exists(file_path):
            self.dump_data(dump_config, extract_trips_minimal())
        _filtered_trips = custom_pickle.load_obj(file_path)
        return _filtered_trips

    def clean_dump(self):
        if self.is_serial:
            delete_dir(self.dump_directory)
            delete_dir(macosx_directory)
            delete_dir(self.log_directory)
            delete_dir(dump_info_directory)

    def dump_data(self, dump_config, param):
        pass


class DumpUtil(DumpUtilBase):
    def dump_data(self, dump_config, operating_trips=None):
        start = datetime.now()
        _filtered_trips = generate_random_dump_data_internal(self.info_enabled, dump_config,
                                                             operating_trips, self.get_suffix())
        self._make_dump_directory()
        dump_file_name = self.dump_directory + dump_config.__key__() + "_" + self.dump_prefix + ".dat"
        custom_pickle.dump_obj(_filtered_trips, dump_file_name)
        end = datetime.now()
        self.update_dump_log(dump_config, start, end)
        return True

    def load_filtered_data(self, dump_config):
        _filtered_trips = self._load_filtered_data(dump_config.base_copy())
        ev_buses, gas_buses = create_buses(dump_config.ev_count, dump_config.gv_count)
        return DumpStructure(_filtered_trips, ev_buses, gas_buses, dump_config.__key__())


class DumpUtilIP(DumpUtil):
    def __init__(self, is_serial=False, log_enabled=True, info_enabled=True):
        super(DumpUtilIP, self).__init__(is_serial, log_enabled, info_enabled)
        self.dump_ip_assist = DumpIPGenAssist()
        self.suffix = "ip"

    def dump_data(self, dump_config, operating_trips=None):
        start = datetime.now()
        dump_util = DumpUtil()  # need to replace this method
        dump_structure = dump_util.load_filtered_data(dump_config)
        mnm_temp_store = self.dump_ip_assist.compute_filtered_data(dump_config, dump_structure)
        dump_structure_lp = DumpStructureIP(dump_structure.filtered_trips, dump_structure.ev_buses,
                                            dump_structure.gas_buses, dump_config.__key__(),
                                            mnm_temp_store)
        self._make_dump_directory()
        dump_file_name = self.dump_directory + dump_config.__key__() + self.get_suffix() + self.dump_prefix + ".dat"
        dump_structure_lp.dump(dump_file_name)
        end = datetime.now()
        self.update_dump_log(dump_config, start, end)
        return True

    def load_filtered_data(self, dump_config):
        return self._load_filtered_data(dump_config)
