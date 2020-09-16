from common.configs.global_constants import key_end
from common.configs.model_constants import electric_bus_type, gas_bus_type, dummy_bus_type


# represents the bus
class Bus(object):
    def __init__(self, bus_name, bus_type):
        self.bus_name = bus_name
        self.bus_type = bus_type

    def __str__(self):
        return self.bus_type.type_name_prefix + ":" + self.bus_name

    def __key__(self):
        return self.bus_type.type_name_prefix + self.bus_name + key_end


# represent the electric bus
class ElectricBus(Bus):
    def __init__(self, bus_name):
        super(ElectricBus, self).__init__(bus_name, electric_bus_type)
        self.energy_unit = "kWh"


# represent the gas bus
class GasBus(Bus):
    def __init__(self, bus_name):
        super(GasBus, self).__init__(bus_name, gas_bus_type)
        self.energy_unit = "gallon(s)"


# represent the dummy bus
# purpose of dummy bus, to provide cost of infinity, if assignment is not succeeded
# with existing vehicles assuming, at optimal state it can have assignments without
# dummy vehicles
class DummyBus(Bus):
    def __init__(self, bus_name):
        super(DummyBus, self).__init__(bus_name, dummy_bus_type)
        self.energy_unit = "unknown"


def bus(bus_name, vehicle_type):
    bus_val = None
    if vehicle_type.type_name == electric_bus_type.type_name:
        bus_val = ElectricBus(bus_name)
    elif vehicle_type.type_name == gas_bus_type.type_name:
        bus_val = GasBus(bus_name)
    elif vehicle_type.type_name == dummy_bus_type.type_name:
        bus_val = DummyBus(bus_name)
    return bus_val


def create_buses(ev_count=3, gv_count=50):
    ev_buses = [bus(str(i), electric_bus_type) for i in range(ev_count)]
    gas_buses = [bus(str(i), gas_bus_type) for i in range(gv_count)]
    return ev_buses, gas_buses


def is_electric(selected_bus):
    _is_electric = False
    if selected_bus.bus_type.type_name == electric_bus_type.type_name:
        _is_electric = True
    return _is_electric


def is_gas(selected_bus):
    _is_gas = False
    if selected_bus.bus_type.type_name == gas_bus_type.type_name:
        _is_gas = True
    return _is_gas


def is_dummy(selected_bus):
    _is_dummy = False
    if selected_bus.bus_type.type_name == dummy_bus_type.type_name:
        _is_dummy = True
    return _is_dummy
