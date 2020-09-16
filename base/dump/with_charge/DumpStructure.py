# -------------------------------------------------------------------------------- #
#                           STRUCTURE OF RANDOM DUMP DATA                          #
# -------------------------------------------------------------------------------- #
from base.dump.DumpStructure import DumpStructureBase


class DumpStructureWTC(DumpStructureBase):
    def __init__(self, filtered_trips, ev_buses, gas_buses, charging, prefix):
        super(DumpStructureWTC, self).__init__(filtered_trips, ev_buses, gas_buses, prefix)
        self.charging = charging


class DumpStructureWTCIP(DumpStructureWTC):
    def __init__(self, filtered_trips, ev_buses, gas_buses, charging, prefix, mnm_temp_store, bus_slot_val_store):
        super(DumpStructureWTCIP, self).__init__(filtered_trips, ev_buses, gas_buses, charging, prefix)
        self.mnm_temp_store = mnm_temp_store
        self.bus_slot_val_store = bus_slot_val_store
