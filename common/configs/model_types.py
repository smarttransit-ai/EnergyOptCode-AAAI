# this used to indicate the type of bus like ELECTRIC, GAS
from common.configs.global_constants import run_mode
from common.mode.RunMode import get_battery_capacity


class BusType(object):
    def __init__(self, type_name, capacity):
        self.type_name = type_name
        self.type_name_prefix = type_name[0]
        self.capacity = capacity


# represent electric bus type
class ElectricBusType(BusType):
    def __init__(self):
        super(ElectricBusType, self).__init__("ELECTRIC", get_battery_capacity(run_mode))


# represent gas bus type
class GasBusType(BusType):
    def __init__(self, capacity=50000):  # capacity can be ignored, just added dummy value
        super(GasBusType, self).__init__("GAS", capacity)


# represent dummy bus type
class DummyBusType(BusType):
    def __init__(self, capacity=10000):  # capacity is not relevant, just added dummy value
        super(DummyBusType, self).__init__("DUMMY", capacity)


# this used to indicate the type of movement like SERVING - represents the OperatingTrip Movement of bus
# MOVING - represents the Trip Movement of bus
class BusMovementType(object):
    def __init__(self, type_name):
        self.type_name = type_name
        self.type_name_prefix = type_name[0:3]


# this was added to differentiate different type of location type, since
# currently only time constraints are prioritize, route point location which denote either start
# or end points are being consider as example type,
class LocationType(object):
    def __init__(self, type_name):
        self.type_name = type_name
