from algo.common.loader import mov_trips
from base.entity.Trip import Trip
from common.Time import add, diff, t_less_or_eq, t_less_than
from common.configs.global_constants import day_code, key_end, cost_of_electricity_per_kwh, \
    cost_of_gas_price_per_gallon, agency_mode, default_dist_tol
from common.configs.model_constants import electric_bus_type, gas_bus_type
from common.mode.RunMode import battery_capacity
from common.mode.ServiceMode import get_range_values


class MovingTripNotExists(Exception):
    def __init__(self, *args):
        super(MovingTripNotExists, self).__init__(args)


def get_energies(_trip_1, _trip_2):
    f_trip = _trip_1
    s_trip = _trip_2
    if t_less_than(_trip_2.start_time, _trip_1.start_time):
        f_trip = _trip_2
        s_trip = _trip_1
    start_pos = f_trip.route.end_pos
    end_pos = s_trip.route.start_pos
    start_time = f_trip.end_time
    time_in_seconds = start_time.time_in_seconds
    time_in_hour = int(start_time.time_in_seconds / 3600)
    mod_time_in_sec = time_in_seconds % 3600
    time_in_hour = time_in_hour if mod_time_in_sec < 1800 else time_in_hour + 1
    start, end = get_range_values(agency_mode, day_code)
    key = (start_pos.lat_lon(), end_pos.lat_lon(), max(start, min(time_in_hour, end - 1)) * 3600)
    if key in mov_trips:
        _, _, mv_trip_electric, mv_trip_gasoline, _ = mov_trips[key]
    else:
        raise MovingTripNotExists("Moving Trip not generated")
    return mv_trip_electric, mv_trip_gasoline


def get_mov_energy(_trip_1, _trip_2, _bus_type):
    energy = 0
    mv_trip_electric, mv_trip_gasoline = get_energies(_trip_1, _trip_2)
    if _bus_type.type_name == electric_bus_type.type_name:
        energy = mv_trip_electric * battery_capacity * 0.01
    elif _bus_type.type_name == gas_bus_type.type_name:
        energy = mv_trip_gasoline
    return energy


def get_mov_cost(_trip_1, _trip_2, _bus_type):
    energy = 0
    mv_trip_electric, mv_trip_gasoline = get_energies(_trip_1, _trip_2)
    if _bus_type.type_name == electric_bus_type.type_name:
        energy = mv_trip_electric * battery_capacity * 0.01 * cost_of_electricity_per_kwh
    elif _bus_type.type_name == gas_bus_type.type_name:
        energy = mv_trip_gasoline * cost_of_gas_price_per_gallon
    return energy


def create_mov_trip(_trip_1, _trip_2):
    if t_less_than(_trip_1.start_time, _trip_2.start_time):
        temp = MovingTrip(_trip_1.route.end_pos, _trip_2.route.start_pos, _trip_1.end_time)
    else:
        temp = MovingTrip(_trip_2.route.end_pos, _trip_1.route.start_pos, _trip_2.end_time)
    return temp.get_instance()


def movable(_trip_1, _trip_2):
    is_movable = False
    expected_start_1 = add(_trip_1.end_time, create_mov_trip(_trip_1, _trip_2).get_duration())
    expected_start_2 = add(_trip_2.end_time, create_mov_trip(_trip_2, _trip_1).get_duration())
    if diff(_trip_2.start_time, expected_start_1).valid:
        is_movable = True
    if diff(_trip_1.start_time, expected_start_2).valid:
        is_movable = True
    return is_movable


def is_in_between(_trip_1, _trip, _trip_2):
    in_between = False
    if _trip.__key__() != _trip_1.__key__() and _trip.__key__() != _trip_2.__key__():
        if movable(_trip_1, _trip) and movable(_trip, _trip_2):
            if t_less_or_eq(_trip_1.end_time, _trip.start_time) and t_less_or_eq(_trip.end_time, _trip_2.start_time):
                in_between = True
            elif t_less_or_eq(_trip_2.end_time, _trip.start_time) and t_less_or_eq(_trip.end_time, _trip_1.start_time):
                in_between = True
    return in_between


class MovingTrip(Trip):
    def __init__(self, start_pos, end_pos, start_time):
        super(MovingTrip, self).__init__(start_pos, end_pos)
        self.set_start_time(start_time)
        self.__trip_create_success = False
        time_in_seconds = start_time.time_in_seconds
        time_in_hour = int(start_time.time_in_seconds / 3600)
        mod_time_in_sec = time_in_seconds % 3600
        time_in_hour = time_in_hour if mod_time_in_sec < 1800 else time_in_hour + 1
        start, end = get_range_values(agency_mode, day_code)
        key = (start_pos.lat_lon(), end_pos.lat_lon(), max(start, min(time_in_hour, end - 1)) * 3600)
        if key in mov_trips:
            mv_trip_duration, mv_trip_distance, mv_trip_electric, mv_trip_gasoline, mv_trip_id = mov_trips[key]
            self.set_distance(mv_trip_distance)
            if mv_trip_distance < default_dist_tol:
                self.add_duration(0)
            else:
                self.add_duration(mv_trip_duration)
            self.add_soc(mv_trip_electric)
            self.add_gasoline_energy(mv_trip_gasoline)
            self.trip_id = mv_trip_id
            self.__trip_create_success = True
        else:
            self.__trip_create_success = False

    def get_instance(self):
        if not self.__trip_create_success:
            raise MovingTripNotExists("Moving Trip not generated")
        return self

    def __str__(self):
        return "MOV_TRIP | " + self.route.__str__()

    def __key__(self):
        # because moving trips are computed for one hour interval
        return "M" + str(self.trip_id) + "S" + self.start_time.time.replace(":", "") + key_end
