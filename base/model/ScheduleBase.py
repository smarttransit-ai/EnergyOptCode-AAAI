from base.entity.Bus import DummyBus
from common.util.common_util import s_print


class ScheduleBase(object):
    def __init__(self, dump_structure, assign_util_config, additional_prefix=""):
        self.assignment = None
        self.assign_util_config = assign_util_config
        self.dump_structure = dump_structure
        self.additional_prefix = additional_prefix
        self.required_assignments = 0
        self.trips_paths = {}

    def schedule(self):
        pass

    def __do_dummy_assign(self):
        operating_trips = self.dump_structure.filtered_trips.copy()
        if self.assign_util_config.dummy_assign:
            if self.required_assignments > 0:
                for trip in operating_trips:
                    dummy_bus = DummyBus(str(self.required_assignments))
                    success = self.assignment.assign(trip, dummy_bus)
                    if success:
                        self.required_assignments -= 1
                        if self.required_assignments == 0:
                            break
            s_print("Dummy Missing Assignments {}".format(str(self.required_assignments)))

    def finalize(self, skip_dummy=False):
        s_print("Expected Dummy Assignments {}".format(str(self.required_assignments)))
        if skip_dummy:
            self.__do_dummy_assign()
        if self.assign_util_config.compute:
            self.assignment.write(self.dump_structure.__key__() + "_" + self.additional_prefix)
            self.assignment.write_bus_stat(self.dump_structure.__key__(), self.additional_prefix,
                                           self.assign_util_config.do_print)
        if self.required_assignments == 0:
            self.assignment.complete = True
