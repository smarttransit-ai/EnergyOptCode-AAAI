# -------------------------------------------------------------------------------- #
#                      GENERATE RANDOM DUMP DATA AND LOADING                       #
# -------------------------------------------------------------------------------- #
from datetime import datetime

from base.dump.DumpUtil import DumpUtilBase, generate_random_dump_data_internal, DumpUtil, DumpUtilIP
from base.dump.with_charge.DumpIPGenAssist import DumpIPGenAssistWTC
from base.dump.with_charge.DumpStructure import DumpStructureWTC, DumpStructureWTCIP
from base.entity.Bus import create_buses
from base.entity.Charging import create_charging
from common.configs.global_constants import with_charging
from common.util import pickle_util as custom_pickle


class DumpUtilWTC(DumpUtilBase):
    def dump_data(self, dump_config, operating_trips=None):
        start = datetime.now()
        _filtered_trips = generate_random_dump_data_internal(self.info_enabled, dump_config,
                                                             operating_trips, self.get_suffix())
        self._make_dump_directory()
        dump_file_name = self.dump_directory + dump_config.__key__() + "_" + self.dump_prefix + ".dat"
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
        self.suffix = "ip"

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
        dump_file_name = self.dump_directory + dump_config.__key__() + self.get_suffix() + self.dump_prefix + ".dat"
        dump_structure_lp.dump(dump_file_name)
        end = datetime.now()
        self.update_dump_log(dump_config, start, end)
        return True

    def load_filtered_data(self, dump_config):
        return self._load_filtered_data(dump_config)


if with_charging:
    dump_util_class = DumpUtilWTC
    dump_util_ip_class = DumpUtilIPWTC
else:
    dump_util_class = DumpUtil
    dump_util_ip_class = DumpUtilIP


class InvalidDumpUtilClassException(Exception):
    def __init__(self, *args):
        super(InvalidDumpUtilClassException, self).__init__(args)


class InvalidDumpUtilIPClassException(Exception):
    def __init__(self, *args):
        super(InvalidDumpUtilIPClassException, self).__init__(args)


def create_dump_util(_dump_util_class, *args):
    if issubclass(_dump_util_class, DumpUtilWTC):
        dump_util = DumpUtilWTC(*args)
    elif issubclass(_dump_util_class, DumpUtil):
        dump_util = DumpUtil(*args)
    else:
        raise InvalidDumpUtilClassException("Invalid DumpUtil Class {}".format(_dump_util_class.__name__))
    return dump_util


def create_dump_util_lp(_dump_util_ip_class, *args):
    if issubclass(_dump_util_ip_class, DumpUtilIPWTC):
        dump_util_lp = DumpUtilIPWTC(*args)
    elif issubclass(_dump_util_ip_class, DumpUtilIP):
        dump_util_lp = DumpUtilIP(*args)
    else:
        raise InvalidDumpUtilIPClassException("Invalid DumpUtilIP Class {}".format(_dump_util_ip_class.__name__))
    return dump_util_lp
