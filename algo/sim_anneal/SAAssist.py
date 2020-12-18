from algo.common.Assist import RunAssist, RunAssistWTC
from algo.sim_anneal.SABase import SimulatedAnnealing
from base.dump.with_charge.DumpUtil import create_dump_util, dump_util_class
from common.configs.global_constants import output_directory, with_charging
from common.parsers.ArgParser import CustomArgParser, CustomWTCArgParser

dump_util = create_dump_util(dump_util_class)


class SAnnealAssist(RunAssist):
    def __init__(self, _dump_util, _output_dir, _skip_ind_summary):
        RunAssist.__init__(self, "sa_cost,sa_emission,sa_time,cycle_count", _dump_util, _output_dir, _skip_ind_summary)

    def _open_writer(self):
        RunAssist._open_writer(self)
        self._write_header()

    def _assist_pre(self, prefix):
        self._path = self._output_dir + prefix + self._suffix + "_summary.csv"
        self._open_writer()

    def _assist_inner(self, args=None):
        sti_anneal = SimulatedAnnealing(self._dump_structure, args)
        self._assignment = sti_anneal.min_assign

    def run(self, prefix, args=None):
        RunAssist.run(self, prefix, CustomArgParser())

    def run_multi(self, prefix, args=None):
        RunAssist.run_multi(self, prefix, CustomArgParser())


class SAnnealAssistWTC(SAnnealAssist, RunAssistWTC):
    def _assist_pre(self, prefix):
        SAnnealAssist._assist_pre(self, prefix)

    def _assist_inner(self, args=None):
        SAnnealAssist._assist_inner(self, args)

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomWTCArgParser())

    def run_multi(self, prefix, args=None):
        RunAssistWTC.run_multi(self, prefix, CustomWTCArgParser())


if with_charging:
    sim_anneal_assist_class = SAnnealAssistWTC
else:
    sim_anneal_assist_class = SAnnealAssist


class InvalidSimAnnealAssistClassException(Exception):
    def __init__(self, *args):
        super(InvalidSimAnnealAssistClassException, self).__init__(args)


def create_sim_anneal_assist(skip_ind_summary=False):
    if issubclass(sim_anneal_assist_class, SAnnealAssistWTC):
        sim_anneal_assist = SAnnealAssistWTC(dump_util, output_directory, _skip_ind_summary=skip_ind_summary)
    elif issubclass(sim_anneal_assist_class, SAnnealAssist):
        sim_anneal_assist = SAnnealAssist(dump_util, output_directory, _skip_ind_summary=skip_ind_summary)
    else:
        raise InvalidSimAnnealAssistClassException(
            "Invalid SAnnealAssist Class {}".format(sim_anneal_assist_class.__name__))
    return sim_anneal_assist
