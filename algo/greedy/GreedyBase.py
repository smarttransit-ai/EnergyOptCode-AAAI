import math
from datetime import datetime

import numpy as np

from algo.common.types import AssignTypes, create_assignment
from base.model.ScheduleBase import ScheduleBase
from base.util.cost_util import init_cost_matrix, update_cost_matrix
from common.util.common_util import s_print


def greedy_assign(dump_structure, assign_util_config, args=None):
    greedy_scheduling = GreedyScheduling(dump_structure, assign_util_config, args)
    greedy_scheduling.schedule()
    greedy_scheduling.finalize()
    return greedy_scheduling.assignment


class GreedyScheduling(ScheduleBase):
    def __init__(self, dump_structure, assign_util_config, args):
        super(GreedyScheduling, self).__init__(dump_structure, assign_util_config, "greedy")
        self.assignment = create_assignment(AssignTypes.GREEDY, dump_structure, args)

    def schedule(self):
        """
            This corresponds to Algorithm 02
            This takes an empty assignment and assign all the trips to the available buses.
        """
        assign_buses = self.dump_structure.all_buses().copy()
        operating_trips = self.dump_structure.filtered_trips.copy()
        self.required_assignments = len(operating_trips)
        assign_type = str(self.assignment.get_type())
        s_print("Expected Assignments {}, Algorithm {}".format(str(self.required_assignments), assign_type))
        start_time = datetime.now()
        _bus_i = None
        _trip_i = None
        operating_trips = sorted(operating_trips, key=lambda trip: trip.start_time.time_in_seconds)
        cost_matrix = init_cost_matrix(self.assignment, operating_trips, assign_buses)
        while self.required_assignments > 0:
            x = np.array(cost_matrix)
            x_min = np.min(x)
            if x_min == math.inf:
                s_print("No more feasible solutions")
                s_print("Remaining trips to be assigned {}".format(str(self.required_assignments)))
                break
            trip_bus_pairs = np.argwhere(x == np.min(x))
            _trip_i, _bus_i = trip_bus_pairs[0]
            _trip = operating_trips[_trip_i]
            _bus = assign_buses[_bus_i]
            self.assignment.assign(_trip, _bus)
            operating_trips.remove(_trip)
            self.required_assignments = len(operating_trips)
            cost_matrix, assignment = update_cost_matrix(self.assignment, operating_trips, assign_buses,
                                                         cost_matrix, _bus_i, _trip_i)
            self.assignment = assignment.copy()
        s_print("{} seconds taken for the computation".format(str((datetime.now() - start_time).total_seconds())))
