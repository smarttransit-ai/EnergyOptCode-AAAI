from enum import Enum

from base.dump.DumpStructure import DumpStructureMissingException
from base.model.with_charge.Assignment import AssignmentWTC


class AssignTypes(Enum):
    GREEDY = 1
    FORCE_UPDATE = 2


class AssignUtilConfig(object):
    def __init__(self, do_shuffle=False, compute=True, do_print=True, dummy_assign=True, time_limit=4):
        self.do_shuffle = do_shuffle
        self.compute = compute
        self.do_print = do_print
        self.dummy_assign = dummy_assign
        self.time_limit = time_limit


def create_assignment(assign_type=None, dump_structure=None, args=None):
    if dump_structure is not None:
        assignment = AssignmentWTC(assign_type, dump_structure.charging)
    else:
        raise DumpStructureMissingException("Dump structure is missing")
    if args is not None:
        assignment.set_weight(args.weight_ev, args.weight_gv)
    return assignment
