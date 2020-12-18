import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.getcwd())

from common.util.common_util import run_function_generic
from common.parsers.ArgParser import CustomWTCArgParser
from base.dump.with_charge.DumpConfig import DumpConfigWTC
from base.dump.with_charge.DumpUtil import DumpUtilWTC
from algo.gen_algo.GenAlgAssist import create_gen_alg_assist
from algo.greedy.GreedyAssist import create_greedy_assist
from algo.sim_anneal.SAAssist import create_sim_anneal_assist
from algo.common.Assist import FUAssist

"""
    here we assign all trips for dates from February till April 10
    using our algorithms
"""

dump_util_main = DumpUtilWTC()
dump_config = DumpConfigWTC(3, 50, 17, 230, 1)
dump_util_main.load_filtered_data(dump_config)

wtc_arg_parser = CustomWTCArgParser()
args = wtc_arg_parser.parse_args().__dict__

start_date = datetime(2020, 2, 3, 3, 0, 0)
end_date = datetime(2020, 4, 11, 3, 0, 0)
over_all_summary = open("over_all_summary.csv", "w+")
over_all_summary.write("date,no_of_trips,real_evs,real_gvs,"
                       "real_ev_assigns,greedy_ev_assigns,sim_anneal_ev_assigns,gen_algo_ev_assigns,"
                       "real_cost,greedy_cost,sim_anneal_cost,gen_algo_cost,"
                       "real_emission,greedy_emission,sim_anneal_emission,gen_algo_emission\n")
over_all_summary.flush()
os.fsync(over_all_summary.fileno())
while start_date != end_date:
    if start_date.weekday() not in [5, 6]:
        custom_output_dir = "result_{}_{}/output/".format(str(start_date.month), str(start_date.day))
        date = start_date.strftime("%Y/%m/%d")

        fu_assist = FUAssist(dump_util_main, custom_output_dir)
        fu_assist.add_params(args)
        fu_assist.update_selected_date(start_date)
        run_function_generic(dump_util_main, func=fu_assist.run_multi, args=("real",))
        real_assign = fu_assist.get_assignment()
        no_of_trips = str(len(real_assign.get_trips()))
        real_evs = str(real_assign.electric_bus_count())
        real_gvs = str(real_assign.gas_bus_count())
        real_ev_assigns = str(real_assign.electric_assign_count())
        real_cost = str(real_assign.total_energy_cost())
        real_emission = str(real_assign.total_emission())

        greedy_assist = create_greedy_assist()
        greedy_assist.add_params(args)
        greedy_assist.update_output_dir(custom_output_dir)
        greedy_assist.inject_real_data_trips(start_date)
        run_function_generic(dump_util_main, func=greedy_assist.run_multi, args=("greedy",))
        greedy_assign = greedy_assist.get_assignment()
        greedy_ev_assigns = str(greedy_assign.electric_assign_count())
        greedy_cost = str(greedy_assign.total_energy_cost())
        greedy_emission = str(greedy_assign.total_emission())

        sim_anneal_assist = create_sim_anneal_assist()
        args["interface"] = "SAAction"
        sim_anneal_assist.add_params(args)
        sim_anneal_assist.update_output_dir(custom_output_dir)
        sim_anneal_assist.inject_real_data_trips(start_date)
        run_function_generic(dump_util_main, func=sim_anneal_assist.run_multi, args=("sim_anneal",))
        sim_anneal_assign = sim_anneal_assist.get_assignment()
        sim_anneal_ev_assigns = str(sim_anneal_assign.electric_assign_count())
        sim_anneal_cost = str(sim_anneal_assign.total_energy_cost())
        sim_anneal_emission = str(sim_anneal_assign.total_energy_cost())

        gen_algo_assist = create_gen_alg_assist()
        args["interface"] = "GAAction"
        gen_algo_assist.add_params(args)
        gen_algo_assist.update_output_dir(custom_output_dir)
        gen_algo_assist.inject_real_data_trips(start_date)
        run_function_generic(dump_util_main, func=gen_algo_assist.run_multi, args=("gen_algo",))
        gen_algo_assign = gen_algo_assist.get_assignment()
        gen_algo_ev_assigns = str(gen_algo_assign.electric_assign_count())
        gen_algo_cost = str(gen_algo_assign.total_energy_cost())
        gen_algo_emission = str(gen_algo_assign.total_emission())

        over_all_summary.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
            date, no_of_trips, real_evs, real_gvs,
            real_ev_assigns, greedy_ev_assigns, sim_anneal_ev_assigns, gen_algo_ev_assigns,
            real_cost, greedy_cost, sim_anneal_cost, gen_algo_cost,
            real_emission, greedy_emission, sim_anneal_emission, gen_algo_emission
        ))
        over_all_summary.flush()
        os.fsync(over_all_summary.fileno())
    start_date = start_date + timedelta(days=1)
over_all_summary.close()
