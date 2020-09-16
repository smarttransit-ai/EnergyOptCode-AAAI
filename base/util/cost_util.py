# -------------------------------------------------------------------------------- #
#                        COMPUTING COST MATRIX FOR GREEDY APPROACH                 #
# -------------------------------------------------------------------------------- #
from base.entity.Bus import is_electric


def init_cost_matrix(assignment, operating_trips, assign_buses):
    """
    Args:
        assignment: the structure that store the assignments of trips to buses
        operating_trips: list of all unassigned trips
        assign_buses: list of all buses
    Returns:
        two dimensional matrix containing the cost of serving each trip t in operating_trips
        by each bus v in assign_buses.
    """
    copy_assign = assignment.copy()
    cost_matrix = [[0 for c_i, _ in enumerate(assign_buses)] for r_i, _ in enumerate(operating_trips)]
    for _trip_i, _trip in enumerate(operating_trips):
        for _bus_i, _bus in enumerate(assign_buses):
            cost_matrix[_trip_i][_bus_i] = copy_assign.biased_energy_cost(_trip, _bus)
    del copy_assign
    return cost_matrix


def update_cost_matrix(assignment, operating_trips, assign_buses, cost_matrix, bus_pos, trip_pos):
    """
    Args:
        assignment: the structure that store the assignments of trips to buses
        operating_trips: list of all unassigned trips
        assign_buses: list of all buses
        cost_matrix: previous cost matrix
        bus_pos: last assigned bus's position in the previous cost matrix
        trip_pos: last assigned trip's position in the previous cost matrix
    Returns:
        two dimensional matrix containing the cost of serving each trip t in operating_trips
        by each bus v in assign_buses.
    """
    import math
    copy_assign = assignment.copy()
    assigned_charging = False
    cost_matrix.pop(trip_pos)
    for _trip_i, _trip in enumerate(operating_trips):
        _bus = assign_buses[bus_pos]
        _info = copy_assign.check(_trip, _bus)
        energy_cost = math.inf
        if _info.feasible():
            energy_cost = copy_assign.biased_energy_cost(_trip, _bus)
        else:
            if is_electric(_bus) and not assigned_charging and \
                    _info.time_feasible() and not _info.energy_feasible():
                _charge_info = copy_assign.assign_charge(_info, _bus, _trip)
                if _charge_info.feasible():
                    _info_new = copy_assign.check(_trip, _bus)
                    if _info_new.feasible():
                        assigned_charging = True
                        assignment.assign_charge_force(_charge_info.entity(), _bus)
                        break
                    else:
                        copy_assign.remove(_charge_info.entity())
        cost_matrix[_trip_i][bus_pos] = energy_cost
    if assigned_charging:
        for _trip_i, _trip in enumerate(operating_trips):
            _bus = assign_buses[bus_pos]
            if copy_assign.check(_trip, _bus).feasible():
                energy_cost = copy_assign.biased_energy_cost(_trip, _bus)
            else:
                energy_cost = math.inf
            cost_matrix[_trip_i][bus_pos] = energy_cost
    del copy_assign
    return cost_matrix, assignment
