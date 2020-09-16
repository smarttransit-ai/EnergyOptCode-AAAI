import os
import sys

sys.path.append(os.getcwd())

from algo.greedy.GreedyAssist import dump_util, create_greedy_assist
from common.util.common_util import run_function_generic

greedy_assist = create_greedy_assist()
greedy_assist.inject_real_data_trips()
run_function_generic(dump_util, func=greedy_assist.run, args=("greedy",))
