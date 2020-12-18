from algo.common.Assist import RunAssist, RunAssistWTC
from algo.gen_algo.GABase import SerialGA
from base.dump.with_charge.DumpUtil import create_dump_util, dump_util_class
from common.configs.global_constants import output_directory, with_charging
from common.parsers.ArgParser import CustomArgParser, CustomWTCArgParser

dump_util = create_dump_util(dump_util_class)


class GenAlgAssist(RunAssist):
    def __init__(self, _dump_util, _output_dir):
        RunAssist.__init__(self, "ga_cost,ga_emission,ga_time,gen_count", _dump_util, _output_dir)
        self.gen_alg = None

    def _open_writer(self):
        RunAssist._open_writer(self)
        self._write_header()

    def _assist_pre(self, prefix):
        self._path = self._output_dir + prefix + self._suffix + "_summary.csv"
        self._open_writer()

    def _assist_inner(self, args=None):
        self.gen_alg = SerialGA(args, self._dump_structure)
        if self.gen_alg.over_all_best is not None:
            self._assignment = self.gen_alg.over_all_best

    def _run_inner(self, parse_args):
        super(GenAlgAssist, self)._run_inner(parse_args)
        self._cur_summary_suffix = [self.get_cost(), self.get_emission(),
                                    self.gen_alg.time_consumed, self.gen_alg.generation_count]

    def run(self, prefix, args=None):
        RunAssist.run(self, prefix, CustomArgParser())

    def run_multi(self, prefix, args=None):
        RunAssist.run_multi(self, prefix, CustomArgParser())


class GenAlgAssistWTC(GenAlgAssist, RunAssistWTC):
    def _assist_pre(self, prefix):
        GenAlgAssist._assist_pre(self, prefix)

    def _assist_inner(self, args=None):
        return GenAlgAssist._assist_inner(self, args)

    def _run_inner(self, parse_args):
        super(GenAlgAssistWTC, self)._run_inner(parse_args)
        self._cur_summary_suffix = [self.get_cost(), self.get_emission(),
                                    self.gen_alg.time_consumed, self.gen_alg.generation_count]

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, CustomWTCArgParser())

    def run_multi(self, prefix, args=None):
        RunAssistWTC.run_multi(self, prefix, CustomWTCArgParser())


if with_charging:
    gen_alg_assist_class = GenAlgAssistWTC
else:
    gen_alg_assist_class = GenAlgAssist


class InvalidGenAlgAssistClassException(Exception):
    def __init__(self, *args):
        super(InvalidGenAlgAssistClassException, self).__init__(args)


def create_gen_alg_assist():
    if issubclass(gen_alg_assist_class, GenAlgAssistWTC):
        gen_alg_assist = GenAlgAssistWTC(dump_util, output_directory)
    elif issubclass(gen_alg_assist_class, GenAlgAssist):
        gen_alg_assist = GenAlgAssist(dump_util, output_directory)
    else:
        raise InvalidGenAlgAssistClassException("Invalid GenAlgAssist Class {}".format(gen_alg_assist_class.__name__))
    return gen_alg_assist
