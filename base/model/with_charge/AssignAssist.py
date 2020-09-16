import os

from base.entity.Bus import is_electric
from base.entity.Charging import Charging
from base.entity.OperatingTrip import OperatingTrip
from base.model.AssignAssist import AssignAssist, generate_new_charge_stat, get_previous_stat, write_bus_stat
from common.configs.global_constants import charging_heading_prefix
from common.configs.model_constants import charging
from common.util.common_util import create_dir


class AssignAssistWTC(AssignAssist):
    def __init__(self, assign):
        super(AssignAssistWTC, self).__init__(assign)

    def write(self, prefix):
        create_dir(self._output_directory)
        all_buses = self._assign.get_buses()
        filtered_trips = []
        _charging = []
        for trip in self._assign.get_trips():
            if isinstance(trip, OperatingTrip):
                filtered_trips.append(trip)
        for s_charging in self._assign.get_charging():
            if isinstance(s_charging, Charging):
                _charging.append(s_charging)

        self._write_assign(filtered_trips, all_buses, prefix)
        self._write_move(all_buses, prefix)
        self.__write_charge(_charging, all_buses, prefix)

    def __write_charge(self, _charging, all_buses, prefix):
        if len(_charging) > 0:
            result_charge = open(self._output_directory + prefix + "/results_charge.csv", "w+")
            charge_heading = charging_heading_prefix
            for _bus in all_buses:
                if is_electric(_bus):
                    charge_heading += _bus.__str__() + ", "
            charge_heading += "\n"
            result_charge.write(charge_heading)
            for s_charging in _charging:
                assigned_bus = self._assign.get(s_charging)
                charge_content = s_charging.__content__()
                for _bus in all_buses:
                    if is_electric(_bus):
                        if assigned_bus is not None and _bus.__key__() == assigned_bus.__key__():
                            charge_content += "1,"
                        else:
                            charge_content += "0,"
                charge_content += "\n"
                result_charge.write(charge_content)
                result_charge.flush()
                os.fsync(result_charge.fileno())
            result_charge.close()

    def write_bus_stat(self, prefix, additional_prefix="", do_print=False):
        total, bus_stats = super(AssignAssistWTC, self)._write_bus_stat(do_print)

        for _charging in self._assign.get_charging():
            if isinstance(_charging, Charging):
                selected_bus = self._assign.get(_charging)
                previous_stat = get_previous_stat(bus_stats, selected_bus)
                new_stat = generate_new_charge_stat(selected_bus, _charging)
                total.add_stat(new_stat, charging)
                previous_stat.add_stat(new_stat, charging)
                bus_stats[selected_bus] = previous_stat

        if do_print:
            for bus_key in bus_stats.keys():
                bus_stat = bus_stats[bus_key]
                bus_stat.print(info=bus_key.__str__())
            total.print()

        write_bus_stat(prefix, self._output_directory, additional_prefix, bus_stats)
