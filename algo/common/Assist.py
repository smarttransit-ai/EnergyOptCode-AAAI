import math
import os
from datetime import datetime

from algo.common.FUBase import ForcedUpdate
from base.dump.DumpConfig import DumpConfig
from base.dump.with_charge.DumpConfig import DumpConfigWTC
from base.entity.Bus import bus
from common.configs.global_constants import run_mode, max_ev_count, max_gv_count, dummy_cost, \
    data_main_directory, trips_directory
from common.configs.global_constants import selected_date
from common.configs.model_constants import electric_bus_type, gas_bus_type
from common.constants import convert_month_day_num_to_str
from common.mode.RunMode import get_r_t_values, get_r_t_h_values, RunMode
from common.parsers.ArgParser import CustomArgParser
from common.parsers.ArgParser import CustomWTCArgParser
from common.util.common_util import create_dir
from common.util.common_util import s_print, run_function_generic
from common.writer.FileWriter import FileWriter


class RunAssist(object):
    def __init__(self, heading, dump_util, output_dir, skip_ind_summary=False):
        self._heading = heading
        self._dump_util = dump_util
        self._output_dir = output_dir
        self._skip_ind_summary = skip_ind_summary
        self._selected_date = None
        self._dump_config = None
        self._dump_structure = None
        self._filtered_trips = None
        self._filtered_trip_ids = None
        self._assignment = None
        self._params = None
        self._cur_summary_suffix = None
        self._path = ""
        self._prefix = ""
        self._suffix = ""
        self.__summary = None

    def add_params(self, params):
        if self._params is None:
            self._params = {}
        self._params.update(params.copy())

    def set_date(self, u_selected_date):
        self._selected_date = u_selected_date

    def set_summary_suffix(self, filename):
        self._suffix = "_" + filename

    def get(self, factor):
        if factor == "cost":
            return self.get_cost()
        elif factor == "emission":
            return self.get_emission()
        else:
            raise ValueError("Invalid factor {}".format(str(factor)))

    def get_cost(self):
        if self._assignment is not None:
            return self._assignment.total_energy_cost()
        else:
            raise TypeError("No assignment object found")

    def get_emission(self):
        if self._assignment is not None:
            return self._assignment.total_emission()
        else:
            raise TypeError("No assignment object found")

    def get_status(self):
        status = "Infeasible"
        if math.floor(self.get_cost() / dummy_cost) == 0:
            status = "Feasible"
        return status

    def inject_trips(self, trips):
        """
        Args:
            trips: update custom filtered trips based on specific trips
        """
        self._filtered_trips = trips.copy()

    def inject_real_data_trips(self, real_world_date=selected_date):
        """
        Args:
            real_world_date: date from which the real world data need to be
                            obtained
        """
        if run_mode == RunMode.FULL:
            import pandas as pd
            day = real_world_date.day
            month = real_world_date.month
            month_val, day_val = convert_month_day_num_to_str(str(month) + "/" + str(day))
            file_name = trips_directory + month_val + "/" + day_val + "/successful.csv"
            if not os.path.exists(file_name):
                fu_assist = FUAssist(self._dump_util, self._output_dir)
                fu_assist.set_date(real_world_date)
                run_function_generic(self._dump_util, func=fu_assist.run, args=("real",))
            df = pd.read_csv(file_name)
            self._filtered_trip_ids = df["trip_id"].to_list()

    def _force_update_trips(self):
        """
            this function is used to considered filtered trips
            instead of all available trips
        """
        if self._filtered_trips is not None:
            self._dump_structure.filtered_trips = self._filtered_trips.copy()
        elif self._filtered_trip_ids is not None:
            filtered_trips = []
            for trip in self._dump_structure.filtered_trips.copy():
                trip_id = trip.get_trip_id(data_type=int)
                if trip_id in self._filtered_trip_ids:
                    filtered_trips.append(trip)
            self._dump_structure.filtered_trips = filtered_trips.copy()

    def update_output_dir(self, _u_output_dir):
        self._output_dir = _u_output_dir

    def get_assignment(self):
        return self._assignment

    def _open_writer(self):
        create_dir(self._output_dir)
        self.__summary = FileWriter(self._path)

    def _write_header(self):
        self.__summary.write_header(self._heading, allow_prefix=True)

    def _write(self, content):
        if not self._skip_ind_summary:
            if self._assignment is not None:
                self._assignment.update_output_dir(self._output_dir)
                self._assignment.write(self._dump_structure.__key__() + "_" + self._prefix)
                self._assignment.write_bus_stat(self._dump_structure.__key__(), self._prefix, do_print=True)
        self.__summary.write(content)

    def _close(self):
        self.__summary.close()
        self._dump_util.clean_dump()

    def _assist_pre(self, prefix):
        raise NotImplementedError

    def _assist_inner(self, args=None):
        raise NotImplementedError

    def _run_inner(self, parse_args):
        self._dump_structure = self._dump_util.load_filtered_data(self._dump_config)
        self._force_update_trips()
        start_time = datetime.now()
        self._assist_inner(parse_args)
        end_time = datetime.now()
        exec_time = (end_time - start_time).total_seconds()
        self._cur_summary_suffix = [self.get_cost(), self.get_emission(), exec_time, self.get_status()]

    def run(self, prefix, args=None):
        self._prefix = prefix
        self._assist_pre(prefix)
        if args is not None and isinstance(args, CustomArgParser):
            parsed_args = args.parse_args()
        else:
            arg_parser = CustomArgParser()
            parsed_args = arg_parser.parse_args()
        e = int(parsed_args.ev_count)
        g = int(parsed_args.gv_count)
        r = int(parsed_args.route_limit)
        t = int(parsed_args.trip_limit)
        self._dump_config = DumpConfig(e, g, r, t)
        self._run_inner(parsed_args)
        self._write([r, t, e, g] + self._cur_summary_suffix)
        self._close()

    def run_multi(self, prefix, args=None):
        self._prefix = prefix
        self._assist_pre(prefix)
        r_t_values = get_r_t_values(run_mode)
        if len(r_t_values) == 0:
            raise ValueError("Empty samp instances !!!")
        for (r, t) in r_t_values:
            e = max_ev_count
            g = min(max_gv_count, 5 * r - e)
            self._dump_config = DumpConfig(e, g, r, t)
            if args is not None and isinstance(args, CustomArgParser):
                parse_args = args.parse_args()
                parse_args.ev_count = e
                parse_args.gv_count = g
                parse_args.route_limit = r
                parse_args.trip_limit = t
                if self._params is not None:
                    parse_args.__dict__.update(self._params.copy())
            else:
                parse_args = args
            self._run_inner(parse_args)
            self._write([r, t, e, g] + self._cur_summary_suffix)
        self._close()

    def print(self):
        s_print("No of Routes : {}".format(str(self._dump_config.route_limit)))
        s_print("No of Trips per route : {}".format(str(self._dump_config.trip_limit)))
        s_print("No of Electric Vehicles : {}".format(str(self._dump_config.ev_count)))
        s_print("No of Gas Vehicles : {}".format(str(self._dump_config.gv_count)))


class RunAssistWTC(RunAssist):
    def __init__(self, heading, dump_util, output_dir):
        RunAssist.__init__(self, heading, dump_util, output_dir)

    def run(self, prefix, args=None):
        self._prefix = prefix
        self._assist_pre(prefix)
        if args is not None and isinstance(args, CustomWTCArgParser):
            parsed_args = args.parse_args()
        else:
            arg_parser = CustomWTCArgParser()
            parsed_args = arg_parser.parse_args()
        e = int(parsed_args.ev_count)
        g = int(parsed_args.gv_count)
        r = int(parsed_args.route_limit)
        t = int(parsed_args.trip_limit)
        h = float(parsed_args.slot_duration)
        self._run_inner(parsed_args)
        self._write([r, t, e, g, h] + self._cur_summary_suffix)
        self._close()

    def run_multi(self, prefix, args=None):
        self._prefix = prefix
        self._assist_pre(prefix)
        r_t_h_values = get_r_t_h_values(run_mode)
        if len(r_t_h_values) == 0:
            raise ValueError("Empty samp instances !!!")
        for (r, t, h) in r_t_h_values:
            e = max_ev_count
            g = min(max_gv_count, 5 * r - e)
            self._dump_config = DumpConfigWTC(e, g, r, t, h)
            if args is not None and isinstance(args, CustomWTCArgParser):
                parse_args = args.parse_args()
                parse_args.ev_count = e
                parse_args.gv_count = g
                parse_args.route_limit = r
                parse_args.trip_limit = t
                parse_args.slot_duration = h
                if self._params is not None:
                    parse_args.__dict__.update(self._params.copy())
            else:
                parse_args = args
            self._run_inner(parse_args)
            self._write([r, t, e, g, h] + self._cur_summary_suffix)
        self._close()

    def _assist_pre(self, prefix):
        raise NotImplementedError

    def _assist_inner(self, args=None):
        raise NotImplementedError

    def print(self):
        RunAssist.print(self)
        s_print("Slot duration : {}".format(self._dump_config.slot_duration))


class FUAssist(RunAssistWTC):
    def __init__(self, _dump_util, _output_dir):
        RunAssistWTC.__init__(self, "fu_cost,fu_emission,fu_time,fu_status", _dump_util, _output_dir)
        self._selected_date = selected_date

    def update_selected_date(self, u_selected_date):
        self._selected_date = u_selected_date

    def _open_writer(self):
        RunAssistWTC._open_writer(self)
        self._write_header()

    def _assist_pre(self, prefix):
        self._path = self._output_dir + prefix + "_summary.csv"
        self._open_writer()

    def _assist_inner(self, args=None):
        dump_config = DumpConfigWTC(3, 50, 17, 230, 1)
        day = self._selected_date.day
        month = self._selected_date.month
        month_val, day_val = convert_month_day_num_to_str(str(month) + "/" + str(day))
        file_name = data_main_directory + "trips/" + month_val + "/" + day_val + ".csv"
        date_str = self._selected_date.strftime("%Y/%m/%d")
        print("Assigning trips to buses as of data for date {}".format(date_str))
        dump_structure = self._dump_util.load_filtered_data(dump_config)
        input_file = open(file_name, "r+")
        lines = input_file.readlines()

        buses_dicts = {}
        for x in range(101, 152):
            buses_dicts[x] = bus(str(x), gas_bus_type)
        for x in range(501, 508):
            buses_dicts[x] = bus(str(x), gas_bus_type)
        for x in range(751, 755):
            buses_dicts[x] = bus(str(x), electric_bus_type)

        trips_dicts = {}
        for trip in dump_structure.filtered_trips:
            trips_dicts[trip.get_trip_id()] = trip

        trip_vehicle_pairs = []
        real_times = {}
        real_times_stamps = {}
        trips = []
        for line in lines[1:]:
            serial, trip_id, vehicle_id, other = line.split(",", 3)
            others = other.split(",")
            start_time_stamp = others[-5]
            end_time_stamp = others[-4]
            start_time = others[-3].split(" ")[1] + ":00"
            end_time = others[-2].split(" ")[1] + ":00"
            route = others[-1]
            current_trip = None
            current_vehicle = None
            start_time_stamp = int(float(start_time_stamp))
            end_time_stamp = int(float(end_time_stamp))
            if route not in ["33", "34", "U", "PI", "PO"]:
                if trip_id in trips_dicts.keys():
                    current_trip = trips_dicts[trip_id]
                if int(vehicle_id) in buses_dicts.keys():
                    current_vehicle = buses_dicts[int(vehicle_id)]
                if start_time_stamp != end_time_stamp:
                    if current_trip in trips:
                        if current_trip is not None and current_vehicle is not None:
                            (p_start_time, p_end_time) = real_times[current_trip.get_trip_id()]
                            (p_start_time_stamp, p_end_time_stamp, p_bus_name) = real_times_stamps[
                                current_trip.get_trip_id()]
                            if p_bus_name == current_vehicle.bus_name:
                                if p_start_time_stamp < start_time_stamp:
                                    start_time_stamp = p_start_time_stamp
                                    start_time = p_start_time
                                if p_end_time_stamp > end_time_stamp:
                                    end_time_stamp = p_end_time_stamp
                                    end_time = p_end_time

                                real_times[current_trip.get_trip_id()] = (start_time, end_time)
                                real_times_stamps[current_trip.get_trip_id()] = (start_time_stamp, end_time_stamp,
                                                                                 current_vehicle.bus_name)
                            else:
                                if int(float(end_time_stamp)) - int(float(start_time_stamp)) >= 300 >= \
                                        int(float(p_end_time_stamp)) - int(float(p_start_time_stamp)):
                                    previous_vehicle = buses_dicts[int(p_bus_name)]
                                    trip_vehicle_pairs.remove([current_trip, previous_vehicle])
                                    trip_vehicle_pairs.append([current_trip, current_vehicle])

                                    real_times[current_trip.get_trip_id()] = (start_time, end_time)
                                    real_times_stamps[current_trip.get_trip_id()] = (start_time_stamp, end_time_stamp,
                                                                                     current_vehicle.bus_name)

                    else:
                        trips.append(current_trip)
                        if current_trip is not None and current_vehicle is not None:
                            trip_vehicle_pairs.append([current_trip, current_vehicle])

                            real_times[current_trip.get_trip_id()] = (start_time, end_time)
                            real_times_stamps[current_trip.get_trip_id()] = (start_time_stamp, end_time_stamp,
                                                                             current_vehicle.bus_name)

        print("Number of filtered trips for forced assign {}".format(str(len(trip_vehicle_pairs))))

        trip_count = 0
        assign_pairs = {}
        for [selected_trip, selected_bus] in trip_vehicle_pairs:
            if selected_trip in trips_dicts.values() and selected_bus in buses_dicts.values():
                trip_count += 1
                time_in_sec = selected_trip.start_s()
                assigns = []
                if time_in_sec in assign_pairs.keys():
                    assigns = assign_pairs[time_in_sec]
                assigns.append((selected_trip, selected_bus))
                assign_pairs[time_in_sec] = assigns.copy()
        specific_trip_dir = trips_directory + month_val + "/" + day_val + "/"
        create_dir(specific_trip_dir)
        fu_assign = ForcedUpdate(dump_structure=dump_structure, result_dir=specific_trip_dir, date=date_str)
        _ = fu_assign.force_update(assign_pairs, real_times=real_times)
        self._assignment = fu_assign.assignment

    def _run_inner(self, parse_args):
        self._dump_config = DumpConfigWTC(3, 50, 17, 230, 1)
        self._dump_structure = self._dump_util.load_filtered_data(self._dump_config)
        self._force_update_trips()
        start_time = datetime.now()
        self._assist_inner(parse_args)
        end_time = datetime.now()
        exec_time = (end_time - start_time).total_seconds()
        self._cur_summary_suffix = [self.get_cost(), self.get_emission(), exec_time, self.get_status()]

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomArgParser())

    def run_multi(self, prefix, args=None):
        RunAssistWTC.run_multi(self, prefix, CustomArgParser())
