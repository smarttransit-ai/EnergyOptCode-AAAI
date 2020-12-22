import os
import sys

sys.path.append(os.getcwd())

from algo.gen_algo.GenAlgAssist import create_gen_alg_assist, dump_util
from common.util.common_util import run_function_generic
from common.configs.global_constants import run_mode
from common.mode.RunMode import RunMode
from common.parsers.ArgParser import ConfigParserCommon

gen_alg_assist = create_gen_alg_assist()
if run_mode == RunMode.FULL:
    gen_alg_assist.inject_real_data_trips()
arg_parser = ConfigParserCommon()
args = arg_parser.parse_args()
args["interface"] = "GAAction"
suffix = args.suffix
if suffix != "":
    gen_alg_assist.set_summary_suffix(suffix)
run_function_generic(dump_util, func=gen_alg_assist.run_multi, args=("gen_alg",))
