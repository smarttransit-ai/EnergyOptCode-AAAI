from collections import namedtuple

from base.entity.Bus import is_dummy
from base.entity.MovingTrip import create_mov_trip
from base.entity.OperatingTrip import OperatingTrip
from base.model.AssignAssist import AssignAssist
from base.model.AssignBase import AssignBase
from base.model.SAAction import SAAction
from common.Time import diff
from common.configs.model_constants import electric_bus_type, gas_bus_type

Weight = namedtuple("Weight", ["weight_ev", "weight_gv"])


class Assignment(AssignBase, SAAction):
    def __init__(self, assignment_type):
        AssignBase.__init__(self)
        SAAction.__init__(self)
        self._assignment_type = assignment_type
        self._d_buses = []
        self._trip_alloc = []
        self._assign_assist = AssignAssist(self)
        self._weight = None
        self.complete = False

    def base_copy(self):
        return Assignment(self._assignment_type)

    def copy(self):
        assign_cpy = Assignment(self._assignment_type)
        assign_cpy._assignments = {}
        assign_cpy._assignments.update(self._assignments.copy())
        for key in self._allocations_dict.keys():
            assign_cpy._allocations_dict[key] = self._allocations_dict[key].copy()
        assign_cpy._count = self._count
        assign_cpy._d_buses = self._d_buses.copy()
        assign_cpy._trip_alloc = self._trip_alloc.copy()
        assign_cpy._weight = self._weight
        assign_cpy.complete = self.complete
        return assign_cpy

    def get_type(self):
        return self._assignment_type

    def reset(self):
        AssignBase.reset(self)
        self._d_buses = []
        self._trip_alloc = []

    def set_weight(self, weight_ev, weight_gv):
        self._weight = Weight(float(weight_ev), float(weight_gv))

    def get_assignment_type(self):
        return self._assignment_type

    def update_output_dir(self, u_output_directory):
        self._assign_assist.update_output_dir(u_output_directory)

    def write(self, prefix):
        self._assign_assist.write(prefix)

    def write_bus_stat(self, prefix, additional_prefix="", do_print=False):
        self._assign_assist.write_bus_stat(prefix, additional_prefix, do_print)

    def assign(self, selected_trip, selected_bus):
        status = False
        if selected_trip not in self._trip_alloc:
            _info = self.add(selected_trip, selected_bus)
            status = _info.feasible()
            if status:
                self._trip_alloc.append(selected_trip)
                if is_dummy(selected_bus):
                    if selected_bus not in self._d_buses:
                        self._d_buses.append(selected_bus)
        return status

    def remove(self, selected_trip):
        remove_status = False
        if selected_trip in self._trip_alloc:
            AssignBase.remove(self, selected_trip)
            if selected_trip in self._trip_alloc:
                self._trip_alloc.remove(selected_trip)
                remove_status = True
        else:
            raise ValueError("remove: trip not exists")
        return remove_status

    def list_bus_allocations(self, selected_bus):
        return super(Assignment, self)._alloc_list(selected_bus)

    def bus_movements(self, selected_bus):
        return super(Assignment, self)._movements(selected_bus)

    def compute_all_movements(self, buses):
        all_movements = []
        for _bus in buses:
            all_movements.append(self.bus_movements(_bus))
        return all_movements

    def total_energy_cost(self):
        all_movements = self.compute_all_movements(self.get_buses())
        summation = 0
        for sel_trip in self.get_trips():
            sel_bus = self.get(sel_trip)
            if isinstance(sel_trip, OperatingTrip):
                summation += sel_trip.get_energy_cost(sel_bus.bus_type)
        for movement_dict in all_movements:
            for movement in movement_dict.keys():
                sel_bus = movement_dict[movement]
                summation += movement.get_energy_cost(sel_bus.bus_type)
        return round(summation, 5)

    def electric_bus_count(self):
        count = 0
        for bus in self.get_buses():
            if bus.bus_type.type_name == electric_bus_type.type_name:
                count += 1
        return count

    def gas_bus_count(self):
        return len(self.get_buses()) - self.electric_bus_count() - len(self._d_buses)

    def electric_assign_count(self):
        count = 0
        for sel_trip in self._assignments.keys():
            sel_bus = self._assignments[sel_trip]
            if sel_bus.bus_type.type_name == electric_bus_type.type_name:
                count += 1
        return count

    def get_buses(self):
        return super(Assignment, self)._values()

    def get_trips(self):
        return super(Assignment, self)._keys()

    def biased_energy_cost(self, selected_trip, selected_bus):
        """
        This corresponds to Algorithm 01
        Args:
            self: set of Assignments
            selected_trip: specific trip
            selected_bus: selected bus to assign to the trip
        Returns:
            biased energy cost for assigning a selected trip to a selected bus
        """
        additional = selected_trip.get_energy_cost(selected_bus.bus_type)
        bus_allocations = self.list_bus_allocations(selected_bus)
        bus_allocations_cpy = bus_allocations.copy()
        bus_allocations_cpy.append(selected_trip)
        bus_allocations_cpy = sorted(bus_allocations_cpy, key=lambda _trip: _trip.start_time.time_in_seconds)
        index = bus_allocations_cpy.index(selected_trip)
        weight = 0
        if selected_bus.bus_type.type_name == electric_bus_type.type_name:
            weight = self._weight.weight_ev
        if selected_bus.bus_type.type_name == gas_bus_type.type_name:
            weight = self._weight.weight_gv
        wait_time_prev = 0
        wait_time_next = 0
        if index > 0:
            prev_assign = bus_allocations_cpy[index - 1]
            mov_trip_1 = create_mov_trip(prev_assign, selected_trip)
            additional += mov_trip_1.get_energy_cost(selected_bus.bus_type)
            wait_time_prev = diff(selected_trip.start_time, prev_assign.end_time).time_in_seconds
        if index < len(bus_allocations_cpy) - 1:
            next_assign = bus_allocations_cpy[index + 1]
            mov_trip_2 = create_mov_trip(selected_trip, next_assign)
            additional += mov_trip_2.get_energy_cost(selected_bus.bus_type)
            wait_time_next = diff(next_assign.start_time, selected_trip.end_time).time_in_seconds
        return additional + (wait_time_prev + wait_time_next) * weight
