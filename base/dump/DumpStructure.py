# -------------------------------------------------------------------------------- #
#                           STRUCTURE OF RANDOM DUMP DATA                          #
# -------------------------------------------------------------------------------- #

from common.util import pickle_util as custom_pickle


class DumpStructureMissingException(Exception):
    def __init__(self, *args):
        super(DumpStructureMissingException, self).__init__(args)


class DumpStructureBase(object):
    def __init__(self, filtered_trips, ev_buses, gas_buses, prefix):
        self.filtered_trips = filtered_trips
        self.ev_buses = ev_buses
        self.gas_buses = gas_buses
        self.__prefix = prefix

    def all_buses(self):
        return self.ev_buses + self.gas_buses

    def __key__(self):
        return self.__prefix

    def dump(self, file_name):
        custom_pickle.dump_obj(self, file_name)

    def load(self, filename):
        obj = custom_pickle.load_obj(filename)
        self.__dict__.update(obj.__dict__.copy())


class DumpStructure(DumpStructureBase):
    def __init__(self, filtered_trips, ev_buses, gas_buses, prefix):
        super(DumpStructure, self).__init__(filtered_trips, ev_buses, gas_buses, prefix)


class DumpStructureIP(DumpStructure):
    def __init__(self, filtered_trips, ev_buses, gas_buses, prefix, mnm_temp_store):
        super(DumpStructureIP, self).__init__(filtered_trips, ev_buses, gas_buses, prefix)
        self.mnm_temp_store = mnm_temp_store
