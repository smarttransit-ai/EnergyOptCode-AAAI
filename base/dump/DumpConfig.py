# -------------------------------------------------------------------------------- #
#                        CONFIGURATION OF RANDOM DUMP DATA                         #
# -------------------------------------------------------------------------------- #
class DumpConfigBase(object):
    def __init__(self, route_limit, trip_limit):
        self.route_limit = route_limit
        self.trip_limit = trip_limit

    def base_copy(self):
        base_config = DumpConfigBase(self.route_limit, self.trip_limit)
        return base_config

    def __key__(self):
        return str(self.route_limit) + "_" + str(self.trip_limit)


class DumpConfig(DumpConfigBase):
    def __init__(self, ev_count, gv_count, route_limit, trip_limit):
        super(DumpConfig, self).__init__(route_limit, trip_limit)
        self.ev_count = ev_count
        self.gv_count = gv_count

    def __key__(self):
        return super(DumpConfig, self).__key__() + "_" + \
               str(self.ev_count) + "_" + str(self.gv_count)
