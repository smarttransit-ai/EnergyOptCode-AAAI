import math

import numpy as np

from base.entity.Bus import is_electric
from base.entity.MovingTrip import is_in_between
from base.entity.OperatingTrip import OperatingTrip
from base.model.AssignBase import AssignBase, FeasibilityStatusInfo
from base.model.Assignment import Assignment
from base.model.CostMatrix import UpdateCostMatrix
from base.model.with_charge.AssignAssist import AssignAssistWTC
from common.configs.model_constants import electric_bus_type
from common.util.common_util import s_print


class NotEnoughEVEnergyException(Exception):
    def __init__(self, *args):
        super(NotEnoughEVEnergyException, self).__init__(*args)


class AssignmentWTC(Assignment):
    def __init__(self, assignment_type, charging_slots):
        Assignment.__init__(self, assignment_type)
        self._charging_slots = charging_slots
        self._charging_alloc = []
        self._assign_assist = AssignAssistWTC(self)

    def reset(self):
        Assignment.reset(self)
        self._charging_alloc = []

    def assign(self, selected_trip, selected_bus):
        status = False
        if selected_trip not in self._trip_alloc:
            _info = self.add(selected_trip, selected_bus)
            if _info.feasible():
                self._trip_alloc.append(selected_trip)
                self._update_stats(selected_bus)
                status = True
            else:
                if is_electric(selected_bus):
                    if _info.time_feasible() and not _info.energy_feasible():
                        _res_info = self.assign_charge(_info, selected_bus, selected_trip)
                        if _res_info.feasible():
                            _res_info_add = self.add(selected_trip, selected_bus)
                            if _res_info_add.feasible():
                                self._trip_alloc.append(selected_trip)
                                self._charging_alloc.append(_res_info.entity())
                                status = True
                    else:
                        if isinstance(selected_trip, OperatingTrip):
                            if electric_bus_type.capacity < selected_trip.get_energy_consumed(electric_bus_type):
                                s_print(_info.energy())
                                raise NotEnoughEVEnergyException("EVBusEnergy is not enough for a single trip !!!")
                        else:
                            s_print(_info.energy())
                            raise NotEnoughEVEnergyException("EVBusEnergy is not enough for a single trip !!!")
            return status

    def assign_charge_force(self, selected_charge, selected_bus):
        _info = FeasibilityStatusInfo()
        if selected_charge not in self._charging_alloc:
            _info = self.add(selected_charge, selected_bus)
            status = _info.feasible()
            if status:
                self._charging_alloc.append(selected_charge)
        return _info

    def assign_charge(self, _info, selected_bus, selected_trip):
        _sel_charging = None
        _adjust_entity = _info.entity()
        possible_charging = []
        for _charging in self._charging_slots:
            if _adjust_entity.start_s() < selected_trip.start_s():
                c0 = is_in_between(_adjust_entity, _charging, selected_trip)
            else:
                c0 = is_in_between(selected_trip, _charging, _adjust_entity)
            c1 = _charging not in self._charging_alloc
            if c0 and c1:
                possible_charging.append(_charging)
        if len(possible_charging) > 0:
            cost_matrix = UpdateCostMatrix(self, possible_charging, [selected_bus])
            x = np.array(cost_matrix.matrix)
            x_min = np.min(x)
            if x_min != math.inf:
                charge_bus_pairs = np.argwhere(x == np.min(x))
                _sel_charging_i, _ = charge_bus_pairs[0]
                _sel_charging = possible_charging[_sel_charging_i]
                _charge_info = self.assign_charge_force(_sel_charging, selected_bus)
                if _charge_info.feasible():
                    _info = FeasibilityStatusInfo(True, True, _sel_charging, 0)
        return _info

    def remove(self, selected_trip):
        remove_status = False
        if selected_trip in self._trip_alloc or selected_trip in self._charging_alloc:
            AssignBase.remove(self, selected_trip)
            if selected_trip in self._trip_alloc:
                self._trip_alloc.remove(selected_trip)
                remove_status = True
            elif selected_trip in self._charging_alloc:
                self._charging_alloc.remove(selected_trip)
                remove_status = True
        else:
            raise ValueError("remove: trip not exists")
        return remove_status

    def base_copy(self):
        base_assign_cpy = AssignmentWTC(self._assignment_type, self._charging_slots.copy())
        base_assign_cpy._weight = self._weight
        return base_assign_cpy

    def copy(self):
        assign_cpy = self.base_copy()
        assign_cpy._assignments = {}
        assign_cpy._assignments.update(self._assignments.copy())
        for key in self._allocations_dict.keys():
            assign_cpy._allocations_dict[key] = self._allocations_dict[key].copy()
        assign_cpy._count = self._count
        assign_cpy._d_buses = self._d_buses.copy()
        assign_cpy._trip_alloc = self._trip_alloc.copy()
        assign_cpy._weight = self._weight
        assign_cpy._charging_alloc = self._charging_alloc.copy()
        assign_cpy.complete = self.complete
        return assign_cpy

    def get_trips(self):
        return self._trip_alloc

    def get_charging(self):
        return self._charging_alloc
