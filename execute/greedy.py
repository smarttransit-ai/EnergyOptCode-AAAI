import os
import sys

sys.path.append(os.getcwd())

from algo.greedy.GreedyAssist import dump_util, create_greedy_assist
from common.util.common_util import run_function_generic
from common.configs.global_constants import run_mode
from common.mode.RunMode import RunMode
from common.parsers.ArgParser import ConfigParserCommon

greedy_assist = create_greedy_assist()
if run_mode == RunMode.FULL:
    greedy_assist.inject_real_data_trips()
arg_parser = ConfigParserCommon()
args = arg_parser.parse_args().__dict__
greedy_assist.add_params(args)
suffix = args["suffix"]
if args["suffix"] != "":
    greedy_assist.set_summary_suffix(suffix)
run_function_generic(dump_util, func=greedy_assist.run_multi, args=("greedy",))
