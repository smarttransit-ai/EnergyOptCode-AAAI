from algo.common.Assist import RunAssist, RunAssistWTC
from algo.int_prog.CustomCPLEX import create_custom_cplex, custom_cplex_class
from algo.int_prog.CustomCPLEXBase import dump_util
from common.configs.global_constants import output_directory, with_charging
from common.util.common_util import run_function_generic


class IPAssist(RunAssist):
    def __init__(self, _dump_util, _output_dir):
        RunAssist.__init__(self, "ip_cost,ip_emission,ip_duration,ip_status_and_gap", _dump_util, _output_dir)

    def _assist_pre(self, prefix):
        self.__dump_util = dump_util
        self._path = self._output_dir + self._suffix + 'ip_summary.csv'
        self._open_writer()
        self._write_header()
        self._prefix = prefix

    def _assist_inner(self, args=None):
        _prefix = self._dump_config.__key__() + "_" + self._prefix.upper()
        self.print()
        my_prob = create_custom_cplex(custom_cplex_class, self._dump_config)
        my_prob.solve_prob()
        objective, status, gap = my_prob.write_summary()
        self._assignment = my_prob.assignment
        self._cur_summary_suffix = ["{} - {} %".format(str(status), str(gap))]

    def get_status(self):
        return self._cur_summary_suffix[0]

    def run(self, prefix, args=None):
        RunAssist.run(self, prefix, args)

    def run_multi(self, prefix, args=None):
        RunAssist.run_multi(self, prefix, args)


class IPAssistWTC(IPAssist, RunAssistWTC):
    def _assist_pre(self, prefix):
        IPAssist._assist_pre(self, prefix)

    def _assist_inner(self, args=None):
        IPAssist._assist_inner(self, args)

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, args)

    def run_multi(self, prefix, args=None):
        RunAssistWTC.run_multi(self, prefix, args)


def generic_program(func, args):
    run_function_generic(dump_util, func=func, args=args)


class InvalidIPAssistClassException(Exception):
    def __init__(self, *args):
        super(InvalidIPAssistClassException, self).__init__(args)


if with_charging:
    ip_assist_class = IPAssistWTC
else:
    ip_assist_class = IPAssist


def create_ip_assist():
    if issubclass(ip_assist_class, IPAssistWTC):
        ip_assist = IPAssistWTC(dump_util, output_directory)
    elif issubclass(ip_assist_class, IPAssist):
        ip_assist = IPAssist(dump_util, output_directory)
    else:
        raise InvalidIPAssistClassException("Invalid IPAssist Class {}".format(ip_assist_class.__name__))
    return ip_assist
