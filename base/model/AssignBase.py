from base.entity.Bus import is_electric
from base.entity.Charging import Charging
from base.entity.MovingTrip import create_mov_trip, movable
from base.entity.OperatingTrip import OperatingTrip
from common.configs.model_constants import electric_bus_type


class FeasibilityStatusInfo(object):
    def __init__(self, time_status=False, energy_status=False, entity=None, energy=0):
        self.__status = time_status and energy_status
        self.__time_status = time_status
        self.__energy_status = energy_status
        self.__entity = entity
        self.__energy = energy

    def set_entity(self, entity):
        self.__entity = entity

    def feasible(self):
        return self.__status

    def time_feasible(self):
        return self.__time_status

    def energy_feasible(self):
        return self.__energy_status

    def entity(self):
        return self.__entity

    def energy(self):
        return self.__energy


class Allocation(object):
    def __init__(self, _val):
        self.__val = _val
        self.__bus_type = _val.bus_type
        self.__allocations = []

    def copy(self):
        alloc = Allocation(self.__val)
        alloc.__allocations = self.__allocations.copy()
        return alloc

    def __key__(self):
        return self.__val.__key__()

    def total_energy(self, _add_entity=None):
        energy = 0
        prev_sel_entity = None
        _all = self.get_list()
        _all_copy = _all.copy()
        if _add_entity is not None:
            _all_copy.append(_add_entity)
        _all_copy = sorted(_all_copy, key=lambda _entity: _entity.start_s())
        _adjust_entity = None
        for i, sel_entity in enumerate(_all_copy):
            if i + 1 < len(_all_copy):
                next_sel_entity = _all_copy[i + 1]
            else:
                next_sel_entity = None
            if prev_sel_entity is not None:
                mov_trip = create_mov_trip(prev_sel_entity, sel_entity)
                energy += mov_trip.get_energy_consumed(self.__bus_type)
            if isinstance(sel_entity, OperatingTrip):
                energy += sel_entity.get_energy_consumed(self.__bus_type)
            elif isinstance(sel_entity, Charging):
                energy = max(0, energy - sel_entity.pole.performance * sel_entity.slot.diff_hours())
            if _add_entity == sel_entity:
                _adjust_entity = prev_sel_entity if prev_sel_entity is not None else next_sel_entity
            prev_sel_entity = sel_entity
        return energy, _adjust_entity

    def __check_feasible(self, _entity):
        energy = 0
        _adjust_entity = None
        if is_electric(self.__val):
            energy, _adjust_entity = self.total_energy(_entity)
            if energy <= electric_bus_type.capacity:
                energy_status = True
            else:
                energy_status = False
        else:
            energy_status = True
        _all = self.get_list()
        _all_copy = _all.copy()
        _all_copy.append(_entity)
        _all_copy = sorted(_all_copy, key=lambda _entity: _entity.start_time.time_in_seconds)
        _pre_sel_entity = None
        time_status = True
        for _sel_entity in _all_copy:
            if _pre_sel_entity is not None:
                if not movable(_pre_sel_entity, _sel_entity):
                    time_status = False
                    break
            _pre_sel_entity = _sel_entity
        return FeasibilityStatusInfo(time_status, energy_status, _adjust_entity, energy)

    def add(self, _entity):
        _info = self.__check_feasible(_entity)
        if _info.feasible():
            self.__allocations.append(_entity)
        return _info

    def check(self, _entity):
        return self.__check_feasible(_entity)

    def remove(self, _entity):
        if _entity in self.__allocations:
            self.__allocations.remove(_entity)
        else:
            raise ValueError("remove: key doesn't exists")

    def get_moves(self):
        used_movements = {}
        allocations = self.get_list()
        allocations = sorted(allocations, key=lambda _entity: _entity.start_time.time_in_seconds)
        for trip_index, previous in enumerate(allocations[:-1]):
            following = allocations[trip_index + 1]
            used_movements[create_mov_trip(previous, following)] = self.__val
        del allocations
        return used_movements

    def get_list(self):
        return self.__allocations.copy()


class GenericInterface(object):
    def base_copy(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def add(self, key, val):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError


class AssignBase(GenericInterface):
    def __init__(self):
        self._assignments = {}
        # Duplicating two variable to reduce the time taken to get allocations
        self._allocations_dict = {}
        self._count = 0

    def reset(self):
        self._assignments = {}
        self._allocations_dict = {}
        self._count = 0

    def __add_allocation(self, _entity, _val):
        alloc_key = _val.__key__()
        if alloc_key in self._allocations_dict.keys():
            allocation = self._allocations_dict.pop(alloc_key)
        else:
            allocation = Allocation(_val)
        _info = allocation.add(_entity)
        self._allocations_dict[alloc_key] = allocation
        return _info

    def add(self, _entity, _val):
        _info = self.__add_allocation(_entity, _val)
        if _info.feasible():
            self._assignments[_entity] = _val
            self._count += 1
        return _info

    def check(self, _entity, _val):
        alloc_key = _val.__key__()
        if alloc_key in self._allocations_dict.keys():
            allocation = self._allocations_dict[alloc_key]
        else:
            allocation = Allocation(_val)
        return allocation.check(_entity)

    def remove(self, _entity):
        if _entity not in self._assignments.keys():
            raise ValueError("remove: trip not exists")
        else:
            _val = self._assignments.pop(_entity)
            alloc_key = _val.__key__()
            if alloc_key in self._allocations_dict.keys():
                allocation = self._allocations_dict.pop(alloc_key)
                allocation.remove(_entity)
                if len(allocation.get_list()) > 0:
                    self._allocations_dict[alloc_key] = allocation
            else:
                raise ValueError("remove_allocation: key doesn't exists")
            self._count -= 1
            status = True
        return status

    def get(self, _entity):
        _val = None
        if _entity in self._assignments:
            _val = self._assignments[_entity]
        return _val

    def get_assignments(self):
        return self._assignments

    def _get_alloc_by_val(self, _val):
        allocation = Allocation(_val)
        alloc_key = allocation.__key__()
        if alloc_key in self._allocations_dict.keys():
            allocation = self._allocations_dict[alloc_key]
        return allocation

    def _alloc_list(self, _val):
        return self._get_alloc_by_val(_val).get_list()

    def _movements(self, _val):
        return self._get_alloc_by_val(_val).get_moves()

    def _total_energy_by_bus(self, _val):
        energy, _ = self._get_alloc_by_val(_val).total_energy()
        return energy

    def _keys(self):
        return self._assignments.keys()

    def _values(self):
        return list(set(self._assignments.values()))

    def copy(self):
        raise NotImplementedError

    def base_copy(self):
        raise NotImplementedError
