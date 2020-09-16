# -------------------------------------------------------------------------------- #
#                        CONFIGURATION OF RANDOM DUMP DATA                         #
# -------------------------------------------------------------------------------- #
from base.dump.DumpConfig import DumpConfig


class DumpConfigWTC(DumpConfig):
    def __init__(self, ev_count, gv_count, route_limit, trip_limit, slot_duration):
        super(DumpConfigWTC, self).__init__(ev_count, gv_count, route_limit, trip_limit)
        self.slot_duration = slot_duration

    def __key__(self):
        return super(DumpConfigWTC, self).__key__() + "_" + str(self.slot_duration).replace(".", "_")
