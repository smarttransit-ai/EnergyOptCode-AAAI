from enum import Enum

from base.dump.DumpStructure import DumpStructureMissingException
from base.interface.GAAction import GAAction
from base.interface.SAAction import SAAction
from base.model.Assignment import Assignment
from base.model.with_charge.Assignment import AssignmentWTC
from common.configs.global_constants import with_charging
from common.util.common_util import s_print


class AssignTypes(Enum):
    GREEDY = 1
    FORCE_UPDATE = 2


class AssignUtilConfig(object):
    def __init__(self, compute=True, do_print=True, dummy_assign=True, time_limit=4):
        self.compute = compute
        self.do_print = do_print
        self.dummy_assign = dummy_assign
        self.time_limit = time_limit


if with_charging:
    assignment_class = AssignmentWTC
else:
    assignment_class = Assignment


class InvalidAssignmentClassException(Exception):
    def __init__(self, *args):
        super(InvalidAssignmentClassException, self).__init__(args)


class AssignmentGA(Assignment, GAAction):
    def base_copy(self):
        base_assign_cpy = AssignmentGA(self._assignment_type)
        base_assign_cpy._weight = self._weight
        return base_assign_cpy


class AssignmentSA(Assignment, SAAction):
    def __init__(self, assignment_type):
        Assignment.__init__(self, assignment_type)
        SAAction.__init__(self)

    def base_copy(self):
        base_assign_cpy = AssignmentSA(self._assignment_type)
        base_assign_cpy._weight = self._weight
        return base_assign_cpy


class AssignmentWTCGA(AssignmentWTC, GAAction):
    def base_copy(self):
        base_assign_cpy = AssignmentWTCGA(self._assignment_type, self._charging_slots.copy())
        base_assign_cpy._weight = self._weight
        return base_assign_cpy


class AssignmentWTCSA(AssignmentWTC, SAAction):
    def __init__(self, assignment_type, charging):
        AssignmentWTC.__init__(self, assignment_type, charging)
        SAAction.__init__(self)

    def base_copy(self):
        base_assign_cpy = AssignmentWTCSA(self._assignment_type, self._charging_slots.copy())
        base_assign_cpy._weight = self._weight
        return base_assign_cpy


def create_assignment(assign_type=None, dump_structure=None, args=None):
    if args is None:
        interface = ""
    else:
        interface = args.interface
    if issubclass(assignment_class, AssignmentWTC):
        if dump_structure is not None:
            if interface == "":
                assignment = AssignmentWTC(assign_type, dump_structure.charging)
            elif interface == "GAAction":
                assignment = AssignmentWTCGA(assign_type, dump_structure.charging)
            elif interface == "SAAction":
                assignment = AssignmentWTCSA(assign_type, dump_structure.charging)
            else:
                raise ValueError("Invalid interface: {}".format(interface))
        else:
            raise DumpStructureMissingException("Dump structure is missing")
    elif issubclass(assignment_class, Assignment):
        if interface == "":
            assignment = Assignment(assign_type)
        elif interface == "GAAction":
            assignment = AssignmentGA(assign_type)
        elif interface == "SAAction":
            assignment = AssignmentSA(assign_type)
        else:
            raise ValueError("Invalid interface: {}".format(interface))
    else:
        raise InvalidAssignmentClassException("Invalid Assignment Class {}".format(assignment_class.__name__))
    if assign_type == AssignTypes.GREEDY:
        if args is not None:
            s_print("Greedy configs: \nev weight: {}\ngv weight: {}".format(args.weight_ev, args.weight_gv))
            assignment.set_weight(args.weight_ev, args.weight_gv)
        else:
            raise ValueError("Missing arguments")
    return assignment
