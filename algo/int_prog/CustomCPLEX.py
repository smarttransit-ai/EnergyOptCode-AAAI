import cplex

from algo.common.CPLEXSupport import CustomCPLEXConstraint, CustomCPLEXVariable
from algo.int_prog.CustomCPLEXBase import CustomCPLEXBase
from base.dump.DumpIPGenAssist import combine_key
from base.entity.Bus import is_electric, is_gas
from base.entity.Charging import create_slots
from base.entity.EnergyConsumed import cost
from base.entity.MovingTrip import get_mov_cost, is_in_between
from base.entity.OperatingTrip import OperatingTrip
from common.configs.global_constants import with_charging
from common.configs.model_constants import electric_bus_type


class CustomCPLEX(CustomCPLEXBase):
    def _set_up_variables(self):
        _mnm_temp_store = self.dump_structure.mnm_temp_store
        _move_trips_pairs = _mnm_temp_store.move_trips_pairs

        variables = []
        costs = []

        for _bus in self.dump_structure.all_buses():
            for _, trip in enumerate(self.dump_structure.filtered_trips):
                variables.append(combine_key([_bus, trip]))
                costs.append(cost(_bus, trip))

        for _bus in self.dump_structure.all_buses():
            for _, (_trip_1, _trip_2) in enumerate(_move_trips_pairs):
                if is_electric(_bus) or (is_gas(_bus) and
                                         isinstance(_trip_1, OperatingTrip) and isinstance(_trip_2, OperatingTrip)):
                    variables.append(combine_key([_bus, _trip_1, _trip_2]))
                    costs.append(get_mov_cost(_trip_1, _trip_2, _bus.bus_type))

        types = [self.variables.type.binary for i, _ in enumerate(variables)]
        ub = [1 for i, _ in enumerate(variables)]
        lb = [0 for i, _ in enumerate(variables)]

        return CustomCPLEXVariable(variables, types, lb, ub, costs)

    def _set_up_constraints(self):
        _buses = self.dump_structure.all_buses()
        _filtered_trips = self.dump_structure.filtered_trips
        _mnm_temp_store = self.dump_structure.mnm_temp_store
        row_names = []
        senses = []
        rhs = []
        row_constraints = []

        '''
        constraints : sum (a_{v,t}) >= 1
        conditions: t | T, v | V
        '''

        for trip in _filtered_trips:
            row_names.append(str("A" + str(self._no_of_const)))
            senses.append("G")
            rhs.append(1)
            pair = cplex.SparsePair(ind=[combine_key([_bus, trip]) for i, _bus in enumerate(_buses)],
                                    val=[1 for i, _ in enumerate(_buses)])
            row_constraints.append(pair)
            self._no_of_const += 1

        '''
        constraints : a_{v,t1} + a_{v,t2} <= 1
        conditions: if ~Feasible, t1,t2 | T, v | V
        '''

        for _bus in self.dump_structure.all_buses():
            for _trip_1, _trip_2 in _mnm_temp_store.n_move_trips_pairs:
                gas_c = isinstance(_trip_1, OperatingTrip) and isinstance(_trip_2, OperatingTrip)
                if is_electric(_bus) or (is_gas(_bus) and gas_c):
                    row_names.append(str("N" + str(self._no_of_const)))
                    senses.append("L")
                    rhs.append(1)
                    assign_1_key = combine_key([_bus, _trip_1])
                    assign_2_key = combine_key([_bus, _trip_2])
                    pair = cplex.SparsePair(ind=[assign_1_key, assign_2_key],
                                            val=[1, 1])
                    row_constraints.append(pair)
                    self._no_of_const += 1

        '''
        constraints : m_{v,t1,t2} - a_{v,t1} - a_{v,t2} + sum (a_{v,t}) >= -1
        conditions: if Feasible, t1,t2 | T; v | V; t | T[t1:t2];
        '''

        _mnm_temp_store = self.dump_structure.mnm_temp_store
        for _bus in self.dump_structure.all_buses():
            for _trip_1, _trip_2 in _mnm_temp_store.move_trips_pairs:
                if is_electric(_bus) or \
                        (is_gas(_bus) and isinstance(_trip_1, OperatingTrip)
                         and isinstance(_trip_2, OperatingTrip)):
                    all_trips = self.get_all_trips()
                    row_names.append(str("M" + str(self._no_of_const)))
                    senses.append("G")
                    rhs.append(-1)
                    assign_1_key = combine_key([_bus, _trip_1])
                    assign_2_key = combine_key([_bus, _trip_2])
                    move_trip_key = combine_key([_bus, _trip_1, _trip_2])

                    ind_temp = [assign_1_key, assign_2_key, move_trip_key]
                    val_temp = [-1, -1, 1]
                    all_trips = sorted(all_trips, key=lambda a_trip: a_trip.start_s())
                    i = all_trips.index(_trip_1)
                    j = all_trips.index(_trip_2)
                    if abs(j - i) > 1:
                        sub_trips = all_trips[i + 1:j]
                        sub_trips = sorted(sub_trips, key=lambda s_trip: s_trip.start_s())
                        for _trip in sub_trips:
                            if is_in_between(_trip_1, _trip, _trip_2):
                                if is_electric(_bus) or (is_gas(_bus) and isinstance(_trip, OperatingTrip)):
                                    trip_key = combine_key([_bus, _trip])
                                    ind_temp.append(trip_key)
                                    val_temp.append(1)
                    pair = cplex.SparsePair(ind=ind_temp.copy(),
                                            val=val_temp.copy())
                    row_constraints.append(pair)
                    self._no_of_const += 1
        return CustomCPLEXConstraint(row_names, senses, rhs, row_constraints)

    def _write_charge(self, prefix):
        pass


class CustomCPLEXWTC(CustomCPLEX):
    def _set_up_variables(self):
        _mnm_temp_store = self.dump_structure.mnm_temp_store
        _move_trips_pairs = _mnm_temp_store.move_trips_pairs

        _custom_var = super(CustomCPLEXWTC, self)._set_up_variables()
        variables = _custom_var.variables
        types = _custom_var.types
        lb = _custom_var.lb
        ub = _custom_var.ub
        costs = _custom_var.costs

        _count = 0
        for _bus in self.dump_structure.ev_buses:
            for _charging in self.dump_structure.charging:
                variables.append(combine_key([_bus, _charging]))
                _count += 1
        types.extend([self.variables.type.binary for _ in range(_count)])
        costs.extend([0 for _ in range(_count)])
        lb.extend([0 for _ in range(_count)])
        ub.extend([1 for _ in range(_count)])

        _ac_count = 0
        slots = create_slots(self.dump_config.slot_duration)
        for _bus in self.dump_structure.ev_buses:
            for i, _slot in enumerate(slots):
                _bs_key = combine_key([_bus, _slot])
                variables.append("CA" + _bs_key)
                _ac_count += 1

        types.extend([self.variables.type.continuous for _ in range(_ac_count)])
        costs.extend([0 for _ in range(_ac_count)])
        lb.extend([0 for _ in range(_ac_count)])
        ub.extend([electric_bus_type.capacity for _ in range(_ac_count)])

        return CustomCPLEXVariable(variables, types, lb, ub, costs)

    def _set_up_constraints(self):
        _mnm_temp_store = self.dump_structure.mnm_temp_store
        _bus_slot_val_store = self.dump_structure.bus_slot_val_store
        slots = create_slots(self.dump_config.slot_duration)

        constraint = super(CustomCPLEXWTC, self)._set_up_constraints()
        row_names = constraint.row_names
        senses = constraint.senses
        rhs = constraint.rhs
        row_constraints = constraint.row_constraints

        '''
        constraints : sum (a_{v,c}) <= 1
        conditions : c | C, v | V, is_electric(v)
        '''

        for _charging in self.dump_structure.charging:
            ind_temp = []
            val_temp = []
            for _bus in self.dump_structure.ev_buses:
                key = combine_key([_bus, _charging])
                ind_temp.append(key)
                val_temp.append(1)

            if len(ind_temp) > 0:
                row_names.append(str("CS" + str(self._no_of_const)))
                senses.append("L")
                rhs.append(1)
                pair = cplex.SparsePair(ind=ind_temp.copy(),
                                        val=val_temp.copy())
                row_constraints.append(pair)
                self._no_of_const += 1

        '''
        constraints : sum (a_{v,c} · P) - c_{v,s} => 0
        conditions : c | C, s | S is_in_slot(c, s); v | V, is_electric(v);
        '''

        for i, slot in enumerate(slots):
            _s_key = combine_key([slot])
            bs_charge_temp_store = _bus_slot_val_store.charge_temp_store
            bs_charge_key_list = bs_charge_temp_store.charge_key_list[_s_key]
            bs_charge_energies = bs_charge_temp_store.charge_energies[_s_key]

            for _bus in self.dump_structure.ev_buses:
                _bs_key = combine_key([_bus, slot])

                if is_electric(_bus):

                    charge_ind_temp = []
                    charge_val_temp = []

                    for charge_key in bs_charge_key_list:
                        charge_key_custom = combine_key([_bus, charge_key])
                        charge_ind_temp.append(charge_key_custom)
                        charge_val_temp.append(bs_charge_energies[charge_key])

                    charge_ind_temp.append("CA" + combine_key([_bus, slot]))
                    charge_val_temp.append(-1)

                    row_names.append(str("CC" + str(self._no_of_const)))
                    senses.append("G")
                    rhs.append(0)
                    pair = cplex.SparsePair(ind=charge_ind_temp.copy(),
                                            val=charge_val_temp.copy())
                    row_constraints.append(pair)
                    self._no_of_const += 1

        '''
        constraints :  0 <=  sum (a_{v,t} * E) + sum (m_{v, t1, t2} * E) - c_{v,s} <= capacity
        conditions : c | C, s | S, is_in_slot(c, s); t, t1, t2 | T; v | V, is_electric(v);
        '''
        for _bus in self.dump_structure.ev_buses:
            ind_temp = []
            val_temp = []

            bs_glb_temp_store = _bus_slot_val_store
            bs_assign_temp_store = bs_glb_temp_store.assign_temp_store
            bs_move_temp_store = bs_glb_temp_store.move_temp_store

            for i, slot in enumerate(slots):

                _s_key = combine_key([slot])
                bs_assign_key_list = bs_assign_temp_store.assign_key_list[_s_key]
                bs_assign_energies = bs_assign_temp_store.assign_energies[_s_key]
                bs_move_key_list = bs_move_temp_store.move_key_list[_s_key]
                bs_move_energies = bs_move_temp_store.move_energies[_s_key]

                _ca_bs_key = "CA" + combine_key([_bus, slot])

                if is_electric(_bus):
                    for assign_key in bs_assign_key_list:
                        assign_key_custom = combine_key([_bus, assign_key])
                        ind_temp.append(assign_key_custom)
                        val_temp.append(bs_assign_energies[assign_key])

                    for move_key in bs_move_key_list:
                        move_key_custom = combine_key([_bus, move_key])
                        ind_temp.append(move_key_custom)
                        val_temp.append(bs_move_energies[move_key])

                    ind_temp.append(_ca_bs_key)
                    val_temp.append(-1)

                    row_names.append(str("CL" + str(self._no_of_const)))
                    senses.append("L")
                    rhs.append(electric_bus_type.capacity)
                    pair = cplex.SparsePair(ind=ind_temp.copy(), val=val_temp.copy())
                    row_constraints.append(pair)
                    self._no_of_const += 1

                    row_names.append(str("CG" + str(self._no_of_const)))
                    senses.append("G")
                    rhs.append(0)
                    pair = cplex.SparsePair(ind=ind_temp.copy(), val=val_temp.copy())
                    row_constraints.append(pair)
                    self._no_of_const += 1

        return CustomCPLEXConstraint(row_names, senses, rhs, row_constraints)


class InvalidCustomCPLEXClassException(Exception):
    def __init__(self, *args):
        super(InvalidCustomCPLEXClassException, self).__init__(args)


if with_charging:
    custom_cplex_class = CustomCPLEXWTC
else:
    custom_cplex_class = CustomCPLEX


def create_custom_cplex(_custom_cplex_class, dump_config, *args):
    if issubclass(_custom_cplex_class, CustomCPLEXWTC):
        custom_cplex = CustomCPLEXWTC(dump_config, *args)
    elif issubclass(_custom_cplex_class, CustomCPLEX):
        custom_cplex = CustomCPLEX(dump_config, *args)
    else:
        raise InvalidCustomCPLEXClassException("Invalid CustomCPLEX Class {}".format(_custom_cplex_class.__name__))
    return custom_cplex
