from algo.common.Assist import RunAssist, RunAssistWTC
from algo.sim_anneal.SABase import SimulatedAnnealing
from base.dump.with_charge.DumpUtil import DumpUtilWTC
from common.configs.global_constants import output_directory
from common.parsers.ArgParser import CustomArgParser, CustomWTCArgParser

dump_util = DumpUtilWTC()


class SAnnealAssist(RunAssist):
    def __init__(self, _dump_util, _output_dir):
        RunAssist.__init__(self, "sa_cost, sa_time, cycle_count", _dump_util, _output_dir)

    def _open_writer(self):
        RunAssist._open_writer(self)
        self._write_header()

    def _assist_pre(self, prefix):
        self._path = self._output_dir + prefix + "_summary.csv"
        self._open_writer()

    def _assist_inner(self, args=None):
        sti_anneal = SimulatedAnnealing(self._dump_structure, args)
        self._assignment = sti_anneal.assignment

    def run(self, prefix, args=None):
        RunAssist.run(self, prefix, CustomArgParser())


class SAnnealAssistWTC(SAnnealAssist, RunAssistWTC):
    def _assist_pre(self, prefix):
        SAnnealAssist._assist_pre(self, prefix)

    def _assist_inner(self, args=None):
        SAnnealAssist._assist_inner(self, args)

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomWTCArgParser())

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomWTCArgParser())


def create_sim_anneal_assist():
    return SAnnealAssistWTC(dump_util, output_directory)
