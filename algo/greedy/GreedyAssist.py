from algo.common.Assist import RunAssist, RunAssistWTC
from algo.common.types import AssignUtilConfig
from algo.greedy.GreedyBase import greedy_assign
from base.dump.with_charge.DumpUtil import DumpUtilWTC
from common.configs.global_constants import output_directory
from common.parsers.ArgParser import CustomWTCArgParser, CustomArgParser

dump_util = DumpUtilWTC()


class GreedyAssist(RunAssist):
    def __init__(self, _dump_util, _output_dir):
        RunAssist.__init__(self, "greedy_cost, greedy_time, greedy_status", _dump_util, _output_dir)

    def _open_writer(self):
        RunAssist._open_writer(self)
        self._write_header()

    def _assist_pre(self, prefix):
        self._path = self._output_dir + prefix + "_summary.csv"
        self._open_writer()

    def _assist_inner(self, args=None):
        self._assignment = greedy_assign(self._dump_structure,
                                         AssignUtilConfig(do_print=True, do_shuffle=True), args=args)

    def run(self, prefix, args=None):
        RunAssist.run(self, prefix, CustomArgParser())


class GreedyAssistWTC(GreedyAssist, RunAssistWTC):
    def _assist_pre(self, prefix):
        GreedyAssist._assist_pre(self, prefix)

    def _assist_inner(self, args=None):
        GreedyAssist._assist_inner(self, args)

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomWTCArgParser())

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomWTCArgParser())


def create_greedy_assist():
    return GreedyAssistWTC(dump_util, output_directory)
