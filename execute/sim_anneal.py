import os
import sys

sys.path.append(os.getcwd())

from algo.sim_anneal.SAAssist import create_sim_anneal_assist, dump_util
from common.util.common_util import run_function_generic
from common.configs.global_constants import run_mode
from common.mode.RunMode import RunMode
from common.parsers.ArgParser import ConfigParserCommon

sim_anneal_assist = create_sim_anneal_assist()
if run_mode == RunMode.FULL:
    sim_anneal_assist.inject_real_data_trips()
arg_parser = ConfigParserCommon()
args = arg_parser.parse_args().__dict__
args["interface"] = "SAAction"
sim_anneal_assist.add_params(args)
suffix = args["suffix"]
if suffix != "":
    sim_anneal_assist.set_summary_suffix(suffix)
run_function_generic(dump_util, func=sim_anneal_assist.run, args=("sim_anneal",))
