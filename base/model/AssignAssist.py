import os

from base.entity.Bus import is_electric, is_gas, is_dummy
from base.entity.OperatingTrip import OperatingTrip
from base.model.BusMovement import BusMovement
from base.model.Stat import InternalStat, BusStat, TotalStat
from common.configs.global_constants import output_directory, bus_stat_heading, trip_heading_prefix
from common.configs.model_constants import serving, moving, charging
from common.util.common_util import create_dir


def generate_new_stat(selected_bus, trip, movement_type):
    bus_duration = trip.get_duration()
    kwh_energy_consumed = 0
    gallon_energy_consumed = 0
    electric_count = 0
    gasoline_count = 0
    bus_energy_consumed = trip.get_energy_consumed(selected_bus.bus_type)
    if is_electric(selected_bus):
        kwh_energy_consumed = bus_energy_consumed
        electric_count = 1
    if is_gas(selected_bus):
        gallon_energy_consumed = bus_energy_consumed
        gasoline_count = 1
    energy_cost = trip.get_energy_cost(selected_bus.bus_type)
    bus_movement = BusMovement(selected_bus, trip, movement_type)
    internal_stat = InternalStat(bus_duration, kwh_energy_consumed, gallon_energy_consumed,
                                 energy_cost, electric_count, gasoline_count)
    new_stat = BusStat(internal_stat, movement_type,
                       {trip.start_time.time_in_seconds: bus_movement})
    return new_stat


def get_previous_stat(bus_stats, selected_bus):
    if selected_bus in bus_stats.keys():
        previous_stat = bus_stats[selected_bus]
    else:
        previous_stat = BusStat()
    return previous_stat


def generate_new_charge_stat(selected_bus, trip):
    bus_movement = BusMovement(selected_bus, trip, charging)
    internal_stat = InternalStat(trip.slot.diff, 0, 0, 0, 1, 0)
    new_stat = BusStat(internal_stat, charging,
                       {trip.slot.start.time_in_seconds: bus_movement})
    return new_stat


def write_bus_stat(prefix, output_dir=output_directory, additional_prefix="", bus_stats=None):
    specific_dir = output_dir + prefix
    if additional_prefix != "":
        specific_dir = specific_dir + "_" + additional_prefix
    create_dir(specific_dir)
    result_bus_stat = open(specific_dir + "/bus_stats.csv", "w+")
    result_bus_stat.write(bus_stat_heading + "\n")
    for _bus in bus_stats:
        if _bus is not None:
            if not is_dummy(_bus):
                bus_stat = bus_stats[_bus]
                bus_stat_content = _bus.__str__() + "," + bus_stat.get_min_csv_line()
                bus_stat_content += "\n"
                result_bus_stat.write(bus_stat_content)
                result_bus_stat.flush()
                os.fsync(result_bus_stat.fileno())
    result_bus_stat.close()


class AssignAssist:
    def __init__(self, assign):
        self._assign = assign
        self._output_directory = output_directory

    def update_output_dir(self, u_output_directory):
        self._output_directory = u_output_directory

    def write(self, prefix):
        create_dir(self._output_directory)
        all_buses = self._assign.get_buses()
        filtered_trips = []
        for trip in self._assign.get_trips():
            if isinstance(trip, OperatingTrip):
                filtered_trips.append(trip)

        self._write_assign(filtered_trips, all_buses, prefix)
        self._write_move(all_buses, prefix)

    def _write_assign(self, filtered_trips, all_buses, prefix):
        if len(filtered_trips) > 0:
            specific_dir = self._output_directory + prefix
            create_dir(specific_dir)
            result_assign = open(specific_dir + "/results_assign.csv", "w+")
            assign_heading = trip_heading_prefix
            for _bus in all_buses:
                assign_heading += _bus.__str__() + ", "
            assign_heading += "\n"
            result_assign.write(assign_heading)
            for trip in filtered_trips:
                assign_content = trip.__content__()
                for _bus in all_buses:
                    if _bus.__key__() == self._assign.get(trip).__key__():
                        assign_content += "1,"
                    else:
                        assign_content += "0,"
                assign_content += "\n"
                result_assign.write(assign_content)
                result_assign.flush()
                os.fsync(result_assign.fileno())
            result_assign.close()

    def _write_move(self, all_buses, prefix):
        all_movements = self._assign.compute_all_movements(self._assign.get_buses())
        if len(all_movements) > 0:
            specific_dir = self._output_directory + prefix
            create_dir(specific_dir)
            result_move = open(specific_dir + "/results_move.csv", "w+")
            move_heading = trip_heading_prefix
            for _bus in all_buses:
                move_heading += _bus.__str__() + ", "
            move_heading += "\n"
            result_move.write(move_heading)
            for movement_dict in all_movements:
                for movement in movement_dict.keys():
                    move_content = movement.__content__()
                    for _bus in all_buses:
                        if _bus.__key__() == movement_dict[movement].__key__():
                            move_content += "1,"
                        else:
                            move_content += "0,"
                    move_content += "\n"
                    result_move.write(move_content)
                    result_move.flush()
                    os.fsync(result_move.fileno())
            result_move.close()

    def _write_bus_stat(self, do_print=False):
        total = TotalStat()
        bus_stats = {}

        # order of precedence is important
        all_movements = self._assign.compute_all_movements(self._assign.get_buses())

        for movement_dict in all_movements:
            for movement in movement_dict.keys():
                selected_bus = movement_dict[movement]
                previous_stat = get_previous_stat(bus_stats, selected_bus)
                new_stat = generate_new_stat(selected_bus, movement, moving)
                total.add_stat(new_stat, moving)
                previous_stat.add_stat(new_stat, moving)
                bus_stats[selected_bus] = previous_stat

        for trip in self._assign.get_trips():
            if isinstance(trip, OperatingTrip):
                selected_bus = self._assign.get(trip)
                previous_stat = get_previous_stat(bus_stats, selected_bus)
                new_stat = generate_new_stat(selected_bus, trip, serving)
                total.add_stat(new_stat, serving)
                previous_stat.add_stat(new_stat, serving)
                bus_stats[selected_bus] = previous_stat

        if do_print:
            for bus_key in bus_stats.keys():
                bus_stat = bus_stats[bus_key]
                bus_stat.print(info=bus_key.__str__())
            total.print()
        return total, bus_stats

    def write_bus_stat(self, prefix, additional_prefix="", do_print=False):
        _, bus_stats = self._write_bus_stat(do_print)
        write_bus_stat(prefix, self._output_directory, additional_prefix, bus_stats)
