from common.configs.global_constants import cost_of_electricity_per_kwh, \
    cost_of_gas_per_gallon, dummy_cost, dummy_energy, co2_emission_per_kwh, co2_emission_per_gallon
from common.configs.model_constants import electric_bus_type, gas_bus_type, dummy_bus_type

# used to indicate the energy consumption
from common.mode.RunMode import battery_capacity


class EnergyConsumed(object):
    def __init__(self, route, vehicle_type):
        self.route = route
        self.type = vehicle_type
        self.energy = 0
        self.cost = 0
        self.co2_emission = 0


# used to indicate the electric energy consumption
class ElectricEnergyConsumed(EnergyConsumed):
    def __init__(self, route):
        super(ElectricEnergyConsumed, self).__init__(route, electric_bus_type)

        self.energy = self.route.soc * battery_capacity * 0.01
        self.cost = self.energy * cost_of_electricity_per_kwh
        self.co2_emission = self.energy * co2_emission_per_kwh


# used to indicate the gas energy consumption
class GasEnergyConsumed(EnergyConsumed):
    def __init__(self, route):
        super(GasEnergyConsumed, self).__init__(route, gas_bus_type)
        self.energy = self.route.gasoline
        self.cost = self.energy * cost_of_gas_per_gallon
        self.co2_emission = self.energy * co2_emission_per_gallon


# used to indicate the dummy energy consumption
class DummyEnergyConsumed(EnergyConsumed):
    def __init__(self, route):
        super(DummyEnergyConsumed, self).__init__(route, dummy_bus_type)
        self.energy = dummy_energy
        self.cost = dummy_cost


def energy_consumed(route, vehicle_type):
    ec_val = None
    if vehicle_type.type_name == electric_bus_type.type_name:
        ec_val = ElectricEnergyConsumed(route)
    elif vehicle_type.type_name == gas_bus_type.type_name:
        ec_val = GasEnergyConsumed(route)
    elif vehicle_type.type_name == dummy_bus_type.type_name:
        ec_val = DummyEnergyConsumed(route)
    return ec_val


def cost(_bus, _trip):
    return energy_consumed(_trip.route, _bus.bus_type).cost


def energy(_bus, _trip):
    return energy_consumed(_trip.route, _bus.bus_type).energy


def emission(_bus, _trip):
    return energy_consumed(_trip.route, _bus.bus_type).co2_emission


def electric_energy(_trip):
    return energy_consumed(_trip.route, electric_bus_type).energy
