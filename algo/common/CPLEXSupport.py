import os
from collections import namedtuple

from cplex import Cplex
from psutil import virtual_memory

from base.dump.DumpIPGenAssist import combine_key
from base.entity.Bus import is_electric
from base.entity.MovingTrip import create_mov_trip, movable
from base.entity.OperatingTrip import OperatingTrip
from common.configs.global_constants import output_directory, charging_heading_prefix, trip_heading_prefix, \
    dump_directory
from common.parsers.ConfigParser import main_conf_parser
from common.util.common_util import create_dir

mem = virtual_memory()
total_mem = mem.total / 1024 ** 2
tree_lim_mem = int(total_mem / 4)
work_lim_mem = int(total_mem / 3.2)

statvfs = os.statvfs(".")
available = statvfs.f_frsize * statvfs.f_bavail
available = available / 1024 ** 2
disk_tree_lim_mem = int(available / 4)
disk_work_lim_mem = int(available / 3.2)

local_dir = main_conf_parser.get_str("IP", "local_dir")
time_limit = main_conf_parser.get_int("IP", "time_limit")

CustomCPLEXVariable = namedtuple('CustomCPLEXVariable', ['variables', 'types', 'lb', 'ub', 'costs'])
CustomCPLEXConstraint = namedtuple('CustomCPLEXConstraint', ['row_names', 'senses', 'rhs', 'row_constraints'])


class CPLEXInterface(Cplex):
    def __init__(self, dump_config, *args):
        super(CPLEXInterface, self).__init__(*args)
        self.ps = None
        self.__configure()
        self.dump_config = dump_config
        self.dump_structure = None
        self.is_integer = None
        self._ip_file_name = dump_directory + dump_config.__key__() + "_ip_model.lp"
        self._load()
        self._no_of_const = 0

    def _load_model(self):
        loaded = False
        if os.path.exists(self._ip_file_name):
            self.variables.delete()
            self.linear_constraints.delete()
            self.read(self._ip_file_name)
            loaded = True
        return loaded

    def _save_model(self):
        create_dir(self._ip_file_name)
        self.write(self._ip_file_name)

    def __inner_configure(self, node_file_ind):
        if node_file_ind == 1:
            self.parameters.mip.limits.treememory.set(tree_lim_mem)
            self.parameters.workmem.set(work_lim_mem)
            self.parameters.mip.strategy.file.set(1)
        elif node_file_ind == 3:
            self.parameters.mip.limits.treememory.set(disk_tree_lim_mem)
            self.parameters.workmem.set(disk_work_lim_mem)
            self.parameters.mip.strategy.file.set(3)

    def __configure(self):
        if os.path.exists(local_dir):
            self.parameters.workdir.set(local_dir)
            self.__inner_configure(3)
        if time_limit != -1:
            self.parameters.timelimit.set(time_limit)
        self.objective.set_name("MinEnergyCost")
        self.objective.set_sense(self.objective.sense.minimize)

    def _load(self):
        raise NotImplementedError

    def get_all_trips(self):
        all_trips = self.dump_structure.filtered_trips.copy()
        if "charging" in self.dump_structure.__dict__.keys():
            all_trips.extend(self.dump_structure.charging.copy())
        return sorted(all_trips, key=lambda trip: trip.start_s())

    def _write_assign(self, prefix):
        variables = self.variables.get_names()
        x = self.solution.get_values()
        _filtered_trips = self.dump_structure.filtered_trips
        _buses = self.dump_structure.all_buses()
        assign_heading = trip_heading_prefix
        result_assign = open(output_directory + prefix + "results_assign.csv", "w+")
        for _bus in _buses:
            assign_heading += _bus.__str__() + ", "
        assign_heading += "\n"
        result_assign.write(assign_heading)
        for trip in _filtered_trips:
            if isinstance(trip, OperatingTrip):
                assign_content = trip.__content__()
                for _bus in _buses:
                    key = combine_key([_bus, trip])
                    temp_value = 0
                    if key in variables:
                        temp_value = x[variables.index(key)]
                    assign_content += str(temp_value) + ","
                assign_content += "\n"
                result_assign.write(assign_content)
                result_assign.flush()
                os.fsync(result_assign.fileno())
        result_assign.close()

    def _write_move(self, prefix):
        variables = self.variables.get_names()
        x = self.solution.get_values()
        _buses = self.dump_structure.all_buses()
        _all_trips = self.get_all_trips()
        result_move = open(output_directory + prefix + "results_move.csv", "w+")
        move_heading = trip_heading_prefix
        for _bus in _buses:
            move_heading += _bus.__str__() + ", "
        move_heading += "\n"
        result_move.write(move_heading)

        for trip_1, trip_2 in self.dump_structure.mnm_temp_store.move_trips_pairs:
            _moving_trip = create_mov_trip(trip_1, trip_2)
            move_content = _moving_trip.__content__()
            for _bus in _buses:
                if movable(trip_1, trip_2) and _moving_trip.route.distance > 0:
                    key = combine_key([_bus, trip_1, trip_2])
                    temp_value = 0
                    if key in variables:
                        temp_value = x[variables.index(key)]
                    move_content += str(temp_value) + ","
            move_content += "\n"
            result_move.write(move_content)
            result_move.flush()
            os.fsync(result_move.fileno())
        result_move.close()

    def _write_charge(self, prefix):
        variables = self.variables.get_names()
        x = self.solution.get_values()
        _buses = self.dump_structure.ev_buses
        _charging = self.dump_structure.charging
        _charge_file_name = output_directory + prefix + "results_charge.csv"
        result_charge = open(_charge_file_name, "w+")
        charge_heading = charging_heading_prefix
        for _bus in _buses:
            if is_electric(_bus):
                charge_heading += _bus.__str__() + ", "
        charge_heading += "\n"
        result_charge.write(charge_heading)
        added_at_least_once = False
        for i, selected_charge in enumerate(_charging):
            add_this_content = False
            charge_content = selected_charge.__content__()
            for _bus in _buses:
                if is_electric(_bus):
                    key = combine_key([_bus, selected_charge])
                    temp_value = 0
                    if key in variables:
                        temp_value = x[variables.index(key)]
                        if temp_value > 0:
                            add_this_content = True
                            added_at_least_once = True
                    charge_content += str(temp_value) + ","
            charge_content += "\n"
            if add_this_content:
                result_charge.write(charge_content)
                result_charge.flush()
                os.fsync(result_charge.fileno())
        result_charge.close()
        if not added_at_least_once:
            os.remove(_charge_file_name)
