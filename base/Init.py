import os
import sys

sys.path.append(os.getcwd())

from base.dump.with_charge.DumpConfig import DumpConfigWTC
from base.dump.with_charge.DumpUtil import DumpUtilIPWTC, DumpUtilWTC
from common.configs.global_constants import run_mode, max_ev_count, max_gv_count, dump_directory
from common.mode.RunMode import get_r_t_h_values, RunMode
from common.util.common_util import create_dir

if run_mode == RunMode.FULL:
    dump_util = DumpUtilWTC()
else:
    dump_util = DumpUtilIPWTC()

create_dir(dump_directory)
for (r, t, h) in get_r_t_h_values(run_mode):
    e = max_ev_count
    g = min(max_gv_count, 5 * r - e)
    dump_config = DumpConfigWTC(e, g, r, t, h)
    dump_util.load_filtered_data(dump_config)
