from datetime import datetime

from algo.common.Assist import RunAssist, RunAssistWTC
from algo.int_prog.CustomCPLEX import CustomCPLEXWTC
from algo.int_prog.CustomCPLEXBase import dump_util
from common.configs.global_constants import output_directory
from common.util.common_util import run_function_generic
from common.util.common_util import s_print


class IPAssist(RunAssist):
    def __init__(self, _dump_util, _output_dir):
        RunAssist.__init__(self, "$ip_cost, $ip_duration, $ip_status", _dump_util, _output_dir)

    def _assist_pre(self, prefix):
        self.__dump_util = dump_util
        self._path = self._output_dir + '$ip_summary.csv'
        self._path = self._path.replace("$ip", prefix)
        self._open_writer()
        self._heading = self._heading.replace("$ip", prefix)
        self._write_header()
        self._prefix = prefix

    def _assist_inner(self, args=None):
        _prefix = self._dump_config.__key__() + "_" + self._prefix.upper()
        prefix = _prefix + "/"
        is_integer = None
        if self._prefix == "ip":
            is_integer = True
        elif self._prefix == "lp":
            is_integer = False
        self.print()
        start_time = datetime.now()
        my_prob = CustomCPLEXWTC(dump_config=self._dump_config)
        my_prob.populate_by_row(is_integer)
        my_prob.solve()
        end_time = datetime.now()
        objective, status = my_prob.write_summary(prefix)
        self._assignment = my_prob.assignment
        duration = (end_time - start_time).total_seconds()
        self._cur_summary_suffix = [objective, duration, status]

    def get_status(self):
        _, _, status = self._cur_summary_suffix
        return status

    def run(self, prefix, args=None):
        RunAssist.run(self, prefix, args)

    def _print_common(self):
        if self._prefix == "ip":
            s_print("Evaluating Integer Programming")
        elif self._prefix == "lp":
            s_print("Evaluating Linear Programming")

    def print(self):
        self._print_common()
        RunAssist.print(self)


class IPAssistWTC(IPAssist, RunAssistWTC):
    def _assist_pre(self, prefix):
        IPAssist._assist_pre(self, prefix)

    def _assist_inner(self, args=None):
        IPAssist._assist_inner(self, args)

    def run(self, prefix, args=None):
        RunAssistWTC.run(self, prefix, args)

    def print(self):
        self._print_common()
        RunAssistWTC.print(self)


def generic_program(func, args):
    run_function_generic(dump_util, func=func, args=args)


class InvalidIPAssistClassException(Exception):
    def __init__(self, *args):
        super(InvalidIPAssistClassException, self).__init__(args)


def create_ip_assist():
    return IPAssistWTC(dump_util, output_directory)
