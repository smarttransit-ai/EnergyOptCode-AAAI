import math
import os
from datetime import datetime

from pandas import DataFrame

from algo.common.constants import convert_month_day_num_to_str
from algo.common.types import AssignTypes, create_assignment
from base.dump.DumpConfig import DumpConfig
from base.dump.with_charge.DumpConfig import DumpConfigWTC
from base.entity.Bus import bus
from base.entity.Charging import Charging
from base.entity.OperatingTrip import OperatingTrip
from common.configs.global_constants import run_mode, max_ev_count, max_gv_count, dummy_cost
from common.configs.model_constants import electric_bus_type, gas_bus_type
from common.mode.RunMode import get_r_t_values, get_r_t_h_values, RunMode
from common.parsers.ArgParser import CustomArgParser
from common.parsers.ArgParser import CustomWTCArgParser
from common.util.common_util import create_dir
from common.util.common_util import s_print, run_function_generic
from common.writer.FileWriter import FileWriter


class RunAssist(object):
    def __init__(self, heading, dump_util, output_dir):
        self._heading = heading
        self._dump_util = dump_util
        self._output_dir = output_dir
        self._dump_config = None
        self._dump_structure = None
        self._filtered_trips = None
        self._filtered_trip_ids = None
        self._assignment = None
        self._ev_weight = None
        self._gv_weight = None
        self._cur_summary_suffix = None
        self._path = ""
        self._prefix = ""
        self.__summary = None

    def get_cost(self):
        if self._assignment is not None:
            return self._assignment.total_energy_cost()
        else:
            raise TypeError("No assignment object found")

    def get_status(self):
        return math.floor(self.get_cost() / dummy_cost)

    def inject_real_data_trips(self, real_world_date=datetime(2020, 3, 2)):
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
            file_name = "real/trips/" + month_val + "/" + day_val + "/successful.csv"
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

    def set_weight(self, ev_weight, gv_weight):
        self._ev_weight = ev_weight
        self._gv_weight = gv_weight

    def get_assignment(self):
        return self._assignment

    def _open_writer(self):
        create_dir(self._output_dir)
        self.__summary = FileWriter(self._path)

    def _write_header(self):
        self.__summary.write_header(self._heading, allow_prefix=True)

    def _write(self, content):
        if self._assignment is not None:
            self._assignment.update_output_dir(self._output_dir)
            self._assignment.write(self._dump_structure.__key__() + "_" + self._prefix)
            self._assignment.write_bus_stat(self._dump_structure.__key__(), self._prefix, do_print=False)
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
        if self._assignment is not None:
            self._cur_summary_suffix = [self.get_cost(), exec_time, self.get_status()]

    def run(self, prefix, args=None):
        self._prefix = prefix
        self._assist_pre(prefix)
        for (r, t) in get_r_t_values(run_mode):
            e = max_ev_count
            g = min(max_gv_count, 5 * r - e)
            self._dump_config = DumpConfig(e, g, r, t)
            if args is not None and isinstance(args, CustomArgParser):
                parse_args = args.parse_args()
                parse_args.ev_count = e
                parse_args.gv_count = g
                parse_args.route_limit = r
                parse_args.trip_limit = t
                if self._ev_weight is not None:
                    parse_args.weight_ev = self._ev_weight
                if self._gv_weight is not None:
                    parse_args.weight_gv = self._gv_weight
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
        for (r, t, h) in get_r_t_h_values(run_mode):
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
                if self._ev_weight is not None:
                    parse_args.weight_ev = self._ev_weight
                if self._gv_weight is not None:
                    parse_args.weight_gv = self._gv_weight
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
        RunAssistWTC.__init__(self, "fu_cost, fu_time, fu_status", _dump_util, _output_dir)
        self._selected_date = None

    def set_date(self, u_selected_date):
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
        file_name = "real/trips/" + month_val + "/" + day_val + ".csv"
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
                time_in_sec = selected_trip.start_time.time_in_seconds
                assigns = []
                if time_in_sec in assign_pairs.keys():
                    assigns = assign_pairs[time_in_sec]
                assigns.append((selected_trip, selected_bus))
                assign_pairs[time_in_sec] = assigns.copy()

        result_dir = file_name.replace(".csv", "/")
        create_dir(result_dir)
        fu_assign = ForcedUpdateBase(dump_structure=dump_structure)
        fu_assign.result_dir = result_dir
        _ = fu_assign.force_update(assign_pairs)
        self._assignment = fu_assign.assignment

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomArgParser())


class ForcedUpdateBase:
    def __init__(self, dump_structure):
        self.assignment = create_assignment(AssignTypes.FORCE_UPDATE, dump_structure=dump_structure)
        self.result_dir = ""

    def force_update(self, _assignments_times=None, skip_success=False):
        failed_count = 0
        trip_ids = []
        if self.assignment.get_type() == AssignTypes.FORCE_UPDATE:
            self.assignment.reset()
            for _assign_pair_key in sorted(_assignments_times.keys()):
                for (_trip, _bus) in _assignments_times[_assign_pair_key]:
                    _info = self.assignment.add(_trip, _bus)
                    if _info.feasible():
                        if isinstance(_trip, OperatingTrip):
                            self.assignment.__dict__["_trip_alloc"].append(_trip)
                            trip_ids.append(_trip.get_trip_id())
                        if isinstance(_trip, Charging):
                            self.assignment.__dict__["_charging_alloc"].append(_trip)
                    else:
                        failed_count += 1
            if not skip_success:
                print("Failed assignments {}".format(str(failed_count)))
                df = DataFrame()
                df["trip_id"] = trip_ids
                df.to_csv(self.result_dir + "successful.csv", index=False)
        else:
            raise NotImplementedError
