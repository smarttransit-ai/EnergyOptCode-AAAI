import os
import sys

sys.path.append(os.getcwd())

from algo.sim_anneal.SAAssist import create_sim_anneal_assist, dump_util
from common.util.common_util import run_function_generic

sim_anneal_assist = create_sim_anneal_assist()
sim_anneal_assist.inject_real_data_trips()
run_function_generic(dump_util, func=sim_anneal_assist.run, args=("sim_anneal",))
