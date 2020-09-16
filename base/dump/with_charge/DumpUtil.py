# -------------------------------------------------------------------------------- #
#                      GENERATE RANDOM DUMP DATA AND LOADING                       #
# -------------------------------------------------------------------------------- #
from datetime import datetime

from base.dump.DumpUtil import DumpUtilBase, generate_random_dump_data_internal
from base.dump.with_charge.DumpIPGenAssist import DumpIPGenAssistWTC
from base.dump.with_charge.DumpStructure import DumpStructureWTC, DumpStructureWTCIP
from base.entity.Bus import create_buses
from base.entity.Charging import create_charging
from common.util import pickle_util as custom_pickle


class DumpUtilWTC(DumpUtilBase):
    def dump_data(self, dump_config, operating_trips=None):
        start = datetime.now()
        _filtered_trips = generate_random_dump_data_internal(self.info_enabled, dump_config, operating_trips)
        self._make_dump_directory()
        dump_file_name = self.dump_directory + dump_config.__key__() + self.dump_prefix + ".dat"
        custom_pickle.dump_obj(_filtered_trips, dump_file_name)
        end = datetime.now()
        self.update_dump_log(dump_config, start, end)
        return True

    def load_filtered_data(self, dump_config):
        _filtered_trips = self._load_filtered_data(dump_config.base_copy())
        ev_buses, gas_buses = create_buses(dump_config.ev_count, dump_config.gv_count)
        _charging = create_charging(dump_config.slot_duration)
        return DumpStructureWTC(_filtered_trips, ev_buses, gas_buses, _charging, dump_config.__key__())


class DumpUtilIPWTC(DumpUtilWTC):
    def __init__(self, is_serial=False, log_enabled=True, info_enabled=True):
        super(DumpUtilIPWTC, self).__init__(is_serial, log_enabled, info_enabled)
        self.dump_ip_gen_assist = DumpIPGenAssistWTC()

    def dump_data(self, dump_config, operating_trips=None):
        start = datetime.now()
        dump_util = DumpUtilWTC()  # need to replace this method
        dump_structure = dump_util.load_filtered_data(dump_config)
        _filtered_trips = dump_structure.filtered_trips
        _ev_buses = dump_structure.ev_buses
        _gas_buses = dump_structure.gas_buses
        _charging = dump_structure.charging

        mnm_temp_store = self.dump_ip_gen_assist.compute_filtered_data(dump_config, dump_structure)
        bus_slot_val_store = self.dump_ip_gen_assist.compute_bus_slot_filtered_data(dump_config, dump_structure)

        dump_structure_lp = DumpStructureWTCIP(_filtered_trips, _ev_buses, _gas_buses, _charging, dump_config.__key__(),
                                               mnm_temp_store, bus_slot_val_store)
        self._make_dump_directory()
        dump_file_name = self.dump_directory + dump_config.__key__() + self.dump_prefix + ".dat"
        dump_structure_lp.dump(dump_file_name)
        end = datetime.now()
        self.update_dump_log(dump_config, start, end)
        return True

    def load_filtered_data(self, dump_config):
        return self._load_filtered_data(dump_config)
