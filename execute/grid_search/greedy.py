import os
import sys

sys.path.append(os.getcwd())

from algo.greedy.GreedyAssist import create_greedy_assist
from common.util.common_util import run_function_generic, grid_search
from common.parsers.ArgParser import CustomWTCArgParser
from base.dump.with_charge.DumpConfig import DumpConfigWTC
from base.dump.with_charge.DumpUtil import DumpUtilWTC

parser = CustomWTCArgParser()
args = parser.parse_args()

dump_util_main = DumpUtilWTC()
dump_config = DumpConfigWTC(3, 50, 17, 230, 1)
dump_util_main.load_filtered_data(dump_config)


def greedy_sub(_i, _j):
    dump_util = DumpUtilWTC()
    greedy_assist = create_greedy_assist()
    greedy_assist.update_output_dir("result_{}_{}/output/".format(str(_i), str(_j)))
    greedy_assist.inject_real_data_trips()
    greedy_assist.set_weight(int(_i), int(_j))
    run_function_generic(dump_util, func=greedy_assist.run, args=("greedy",))


grid_search(greedy_sub)
