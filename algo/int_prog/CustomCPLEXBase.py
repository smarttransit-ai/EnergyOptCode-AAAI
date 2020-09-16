import os
from collections import namedtuple

import cplex
from cplex import Cplex

from algo.common.Assist import ForcedUpdateBase
from base.dump.DumpIPGenAssist import combine_key
from base.dump.with_charge.DumpUtil import DumpUtilIPWTC
from common.configs.global_constants import dump_directory, output_directory
from common.util.common_util import create_dir

dump_util = DumpUtilIPWTC()

CustomCPLEXVariable = namedtuple('CustomCPLEXVariable', ['variables', 'types', 'lb', 'ub', 'costs'])
CustomCPLEXConstraint = namedtuple('CustomCPLEXConstraint', ['row_names', 'senses', 'rhs', 'row_constraints'])


class CustomCPLEXBase(Cplex):
    def __init__(self, dump_config, *args):
        super(CustomCPLEXBase, self).__init__(*args)
        self.__configure()
        self.dump_config = dump_config
        self.dump_structure = None
        self.is_integer = None
        self.assignment = None
        self.__ip_file_name = dump_directory + dump_config.__key__() + "_$ip_model.lp"
        self.__load()
        self._no_of_const = 0

    def _load_model(self, prefix):
        loaded = False
        self.__ip_file_name = self.__ip_file_name.replace("$ip", prefix)
        if os.path.exists(self.__ip_file_name):
            self.variables.delete()
            self.linear_constraints.delete()
            self.read(self.__ip_file_name)
            loaded = True
        return loaded

    def _save_model(self, prefix):
        self.__ip_file_name = self.__ip_file_name.replace("$ip", prefix)
        create_dir(self.__ip_file_name)
        self.write(self.__ip_file_name)

    def __configure(self):
        self.objective.set_name("MinEnergyCost")
        self.objective.set_sense(self.objective.sense.minimize)

    def __load(self):
        self.dump_structure = dump_util.load_filtered_data(self.dump_config)

    def get_all_trips(self):
        all_trips = self.dump_structure.filtered_trips.copy()
        if "charging" in self.dump_structure.__dict__.keys():
            all_trips.extend(self.dump_structure.charging.copy())
        return sorted(all_trips, key=lambda trip: trip.start_time.time_in_seconds)

    def populate_by_row(self, is_integer=True):
        if is_integer:
            prefix = "IP"
        else:
            prefix = "LP"
        self.is_integer = is_integer
        if not self._load_model(prefix):
            variable = self._set_up_variables(is_integer)
            variables = variable.variables
            types = variable.types
            lb = variable.lb
            ub = variable.ub
            costs = variable.costs
            self.variables.add(obj=costs, ub=ub, lb=lb, names=variables, types=types)
            constraint = self._set_up_constraints()
            row_constraints = constraint.row_constraints
            senses = constraint.senses
            rhs = constraint.rhs
            row_names = constraint.row_names
            self.linear_constraints.add(lin_expr=row_constraints, senses=senses, rhs=rhs, names=row_names)
            self._save_model(prefix)

    def get_obj_status(self):
        objective = "NA"
        print("Solution status = ", self.solution.get_status(), ":", end=' ')
        status = self.solution.status[self.solution.get_status()]
        try:
            objective = round(self.solution.get_objective_value(), 5)
            print("Solution value  = ", objective)
        except cplex.exceptions.errors.CplexSolverError:
            exit(-1)
        return objective, status

    def write_summary(self, prefix):
        objective, status = self.get_obj_status()

        # this is only works fine for whole number assignments
        # so linear program cannot be supported using this
        if self.is_integer:
            variables = self.variables.get_names()
            x = self.solution.get_values()
            _buses = self.dump_structure.all_buses()

            _all_trips = self.get_all_trips()
            assign_pairs = {}
            for i, selected_trip in enumerate(_all_trips):
                for _bus in _buses:
                    key = combine_key([_bus, selected_trip])
                    if key in variables:
                        trip_assign_value = x[variables.index(key)]
                        if trip_assign_value == 1.0:
                            time_in_sec = selected_trip.start_time.time_in_seconds
                            assigns = []
                            if time_in_sec in assign_pairs.keys():
                                assigns = assign_pairs[time_in_sec]
                            assigns.append((selected_trip, _bus))
                            assign_pairs[time_in_sec] = assigns
            fu_assign = ForcedUpdateBase(dump_structure=self.dump_structure)
            fu_assign.force_update(assign_pairs, skip_success=True)
            self.assignment = fu_assign.assignment
        else:
            create_dir(output_directory + prefix)
            self._write_assign(prefix)
            self._write_move(prefix)
            self._write_charge(prefix)
        return objective, status

    def _set_up_variables(self, is_integer):
        raise NotImplementedError

    def _set_up_constraints(self):
        raise NotImplementedError

    def _write_assign(self, prefix):
        raise NotImplementedError

    def _write_move(self, prefix):
        raise NotImplementedError

    def _write_charge(self, prefix):
        raise NotImplementedError
