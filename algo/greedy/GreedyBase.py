import math
import random
from datetime import datetime

import numpy as np

from algo.common.types import AssignTypes, create_assignment
from base.model.CostMatrix import CostMatrix
from base.model.ScheduleBase import ScheduleBase
from common.util.common_util import s_print


def greedy_assign(dump_structure, assign_util_config, args=None, random_order=False):
    greedy_scheduling = GreedyScheduling(dump_structure, assign_util_config, args, random_order)
    greedy_scheduling.schedule()
    greedy_scheduling.finalize()
    return greedy_scheduling.assignment


class GreedyScheduling(ScheduleBase):
    def __init__(self, dump_structure, assign_util_config, args=None, random_order=False):
        super(GreedyScheduling, self).__init__(dump_structure, assign_util_config, "greedy")
        self.assignment = create_assignment(assign_type=AssignTypes.GREEDY, dump_structure=dump_structure, args=args)
        self.random_order = random_order

    # this approach find the minimum cost based on all assignments
    def schedule(self):
        assign_buses = self.dump_structure.all_buses().copy()
        operating_trips = self.dump_structure.filtered_trips.copy()
        self.required_assignments = len(operating_trips)
        assign_type = str(self.assignment.get_type())
        s_print("Expected Assignments {}, Algorithm {}".format(str(self.required_assignments), assign_type))
        start_time = datetime.now()
        if self.random_order:
            random.shuffle(operating_trips)
        else:
            operating_trips = sorted(operating_trips, key=lambda trip: trip.start_s())
        cost_matrix = CostMatrix(self.assignment, operating_trips, assign_buses)
        while self.required_assignments > 0:
            assigned = False
            _bus_i = -1
            _trip_i = -1
            np_cost_matrix = np.array(cost_matrix.matrix)
            min_cost = np.min(np_cost_matrix)
            if min_cost == math.inf:
                s_print("No more feasible solutions")
                s_print("Remaining trips to be assigned {}".format(str(self.required_assignments)))
                break
            feasible_assign_pairs = np.argwhere(np_cost_matrix == min_cost)
            _trip_i, _bus_i = feasible_assign_pairs[0]
            _trip = operating_trips[_trip_i]
            _bus = assign_buses[_bus_i]
            if (_trip, _bus) in cost_matrix.req_charging.keys():
                _charging = cost_matrix.req_charging[_trip, _bus]
                if self.assignment.assign_charge_force(_charging, _bus):
                    if self.assignment.assign(_trip, _bus):
                        assigned = True
            elif self.assignment.assign(_trip, _bus):
                assigned = True

            if assigned:
                self.required_assignments -= 1
                cost_matrix.update(self.assignment, _bus_i, _trip_i)
            else:
                s_print("Not Assigned !!! No more feasible solutions")
                s_print("Remaining trips to be assigned {}".format(str(self.required_assignments)))
                break
        s_print("{} seconds taken for the computation".format(str((datetime.now() - start_time).total_seconds())))
