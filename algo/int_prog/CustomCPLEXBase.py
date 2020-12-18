import cplex

from algo.common.CPLEXSupport import CPLEXInterface
from algo.common.FUBase import ForcedUpdateBase
from base.dump.DumpIPGenAssist import combine_key
from base.dump.with_charge.DumpUtil import create_dump_util_lp, dump_util_ip_class
from common.util.common_util import s_print_err, s_print

dump_util = create_dump_util_lp(dump_util_ip_class)


class CustomCPLEXBase(CPLEXInterface):
    def __init__(self, dump_config, *args):
        super(CustomCPLEXBase, self).__init__(dump_config, *args)
        self.assignment = None

    def _load(self):
        self.dump_structure = dump_util.load_filtered_data(self.dump_config)

    def solve_prob(self):
        if not self._load_model():
            variable = self._set_up_variables()
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
            self._save_model()
        self.solve()

    def get_obj_status(self):
        objective = "NA"
        gap = "NA"
        s_print("Solution status = " + str(self.solution.get_status()) + ":", end=False)
        status = self.solution.status[self.solution.get_status()]
        try:
            objective = round(self.solution.get_objective_value(), 5)
            gap = round(self.solution.MIP.get_mip_relative_gap() * 100, 2)
            s_print("Solution value  = " + str(objective))
        except cplex.exceptions.errors.CplexSolverError:
            s_print_err("Solution not exists exiting the program")
            exit(-1)
        return objective, status, gap

    def write_summary(self):
        objective, status, gap = self.get_obj_status()
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
                        time_in_sec = selected_trip.start_s()
                        assigns = []
                        if time_in_sec in assign_pairs.keys():
                            assigns = assign_pairs[time_in_sec]
                        assigns.append((selected_trip, _bus))
                        assign_pairs[time_in_sec] = assigns
        fu_assign = ForcedUpdateBase(dump_structure=self.dump_structure)
        fu_assign.force_update(assign_pairs)
        self.assignment = fu_assign.assignment
        return objective, status, gap

    def _set_up_variables(self):
        raise NotImplementedError

    def _set_up_constraints(self):
        raise NotImplementedError
