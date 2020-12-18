# -------------------------------------------------------------------------------- #
#                       COMPUTING COST MATRIX FOR GREEDY APPROACH                  #
# -------------------------------------------------------------------------------- #
from base.entity.Bus import is_electric


class CostMatrix:
    def __init__(self, assignment, operating_trips, assign_buses):
        """
        Args:
            assignment: the structure that store the assignments of trips to buses
            operating_trips: list of all operating trips
            assign_buses: list of all buses
        Returns:
            two dimensional matrix containing the cost of serving each trip t in operating_trips
            by each bus v in assign_buses.
        """
        self.operating_trips = operating_trips
        self.assign_buses = assign_buses
        self.matrix = [[0 for v_i, _ in enumerate(assign_buses)] for t_i, _ in enumerate(operating_trips)]
        self.req_charging = {}
        self.init(assignment)

    def init(self, assignment):
        """
        Args:
            assignment: the structure that store the assignments of trips to buses
        """
        for _trip_i, _trip in enumerate(self.operating_trips):
            for _bus_i, _bus in enumerate(self.assign_buses):
                self.matrix[_trip_i][_bus_i] = assignment.energy_cost(_trip, _bus)

    def update(self, assignment, bus_pos, trip_pos):
        """
        Args:
            assignment: the structure that store the assignments of trips to buses
            trip_pos: last assigned trip's position
            bus_pos: last assigned bus's position
        Returns:
            two dimensional matrix containing the cost of serving each trip t in operating_trips
            by each bus v in assign_buses.
        """
        import math
        self.matrix.pop(trip_pos)
        prev_trip = self.operating_trips.pop(trip_pos)
        clean_keys = []
        for trip, bus in self.req_charging.keys():
            if trip == prev_trip:
                clean_keys.append((trip, bus))
        for key in clean_keys:
            self.req_charging.pop(key)
        for _trip_i, _trip in enumerate(self.operating_trips):
            _bus = self.assign_buses[bus_pos]
            copy_assign = assignment.copy()
            _info = copy_assign.check(_trip, _bus)
            energy_cost = math.inf
            if _info.feasible():
                energy_cost = copy_assign.energy_cost(_trip, _bus)
            else:
                if is_electric(_bus) and _info.time_feasible() and not _info.energy_feasible():
                    _charge_info = copy_assign.assign_charge(_info, _bus, _trip)
                    if _charge_info.feasible():
                        _info_new = copy_assign.check(_trip, _bus)
                        if _info_new.feasible():
                            energy_cost = copy_assign.energy_cost(_trip, _bus)
                            self.req_charging[_trip, _bus] = _charge_info.entity()
            self.matrix[_trip_i][bus_pos] = energy_cost
            del copy_assign


class UpdateCostMatrix(CostMatrix):
    def init(self, assignment):
        """
        Args:
            assignment: the structure that store the assignments of trips to buses
        """
        import math
        for _trip_i, _trip in enumerate(self.operating_trips):
            for _bus_i, _bus in enumerate(self.assign_buses):
                copy_assign = assignment.copy()
                energy_cost = math.inf
                _info = copy_assign.check(_trip, _bus)
                if _info.feasible():
                    energy_cost = copy_assign.energy_cost(_trip, _bus)
                self.matrix[_trip_i][_bus_i] = energy_cost
