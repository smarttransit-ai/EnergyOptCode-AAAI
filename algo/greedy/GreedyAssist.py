from algo.common.Assist import RunAssist, RunAssistWTC
from algo.common.types import AssignUtilConfig
from algo.greedy.GreedyBase import greedy_assign
from base.dump.with_charge.DumpUtil import dump_util_class, create_dump_util
from common.configs.global_constants import output_directory, with_charging
from common.parsers.ArgParser import CustomWTCArgParser, CustomArgParser

dump_util = create_dump_util(dump_util_class)


class GreedyAssist(RunAssist):
    def __init__(self, _dump_util, _output_dir, _skip_ind_summary):
        RunAssist.__init__(self, "greedy_cost,greedy_emission,greedy_time,greedy_status",
                           _dump_util, _output_dir, _skip_ind_summary)

    def _open_writer(self):
        RunAssist._open_writer(self)
        self._write_header()

    def _assist_pre(self, prefix):
        self._path = self._output_dir + prefix + self._suffix + "_summary.csv"
        self._open_writer()

    def _assist_inner(self, args=None):
        self._assignment = greedy_assign(self._dump_structure,
                                         AssignUtilConfig(do_print=True), args=args)

    def run(self, prefix, args=None):
        RunAssist.run(self, prefix, CustomArgParser())

    def run_multi(self, prefix, args=None):
        RunAssist.run_multi(self, prefix, CustomArgParser())


class GreedyAssistWTC(GreedyAssist, RunAssistWTC):
    def _assist_pre(self, prefix):
        GreedyAssist._assist_pre(self, prefix)

    def _assist_inner(self, args=None):
        GreedyAssist._assist_inner(self, args)

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomWTCArgParser())

    def run_multi(self, prefix, args=None):
        RunAssistWTC.run_multi(self, prefix, CustomWTCArgParser())


if with_charging:
    greedy_assist_class = GreedyAssistWTC
else:
    greedy_assist_class = GreedyAssist


class InvalidGreedyAssistClassException(Exception):
    def __init__(self, *args):
        super(InvalidGreedyAssistClassException, self).__init__(args)


def create_greedy_assist(skip_ind_summary=False):
    if issubclass(greedy_assist_class, GreedyAssistWTC):
        greedy_assist = GreedyAssistWTC(dump_util, output_directory, _skip_ind_summary=skip_ind_summary)
    elif issubclass(greedy_assist_class, GreedyAssist):
        greedy_assist = GreedyAssist(dump_util, output_directory, _skip_ind_summary=skip_ind_summary)
    else:
        raise InvalidGreedyAssistClassException(
            "Invalid GreedyAssist Class {}".format(greedy_assist_class.__name__))
    return greedy_assist
