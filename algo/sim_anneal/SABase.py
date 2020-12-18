import math
import random

from algo.common.types import AssignUtilConfig
from algo.common.util import nearest_neighbour
from algo.greedy.GreedyBase import greedy_assign
from common.configs.global_constants import summary_directory
from common.util.common_util import s_print, create_dir
from common.writer.FileWriter import FileWriter


class SimulatedAnnealing:
    def __init__(self, dump_structure, args):
        self.min_assign = None
        self.min_cost = None
        self.summary_file_name = ""
        self.run(dump_structure, args)

    def run(self, dump_structure, args):
        cycle_count = int(args.cycle_count)
        start_prob = float(args.start_prob)
        end_prob = float(args.end_prob)
        swap_prob = float(args.swap_prob)

        swap_condition = 0 < swap_prob < 1
        start_end_condition = 0 < end_prob < start_prob < 1

        s_print("Simulated annealing configs: \ncycle Count: {}\nstart prob: {}\nend prob: {}\nswap prob: {}".
                format(args.cycle_count, args.start_prob, args.end_prob, args.swap_prob))

        if not swap_condition or not start_end_condition:
            raise ValueError("inconsistent parameters")

        assignment = greedy_assign(dump_structure, AssignUtilConfig(do_print=True), args=args)
        energy_cost = assignment.total_energy_cost()
        self.min_assign = assignment
        self.min_cost = energy_cost

        temp_start = -1.0 / math.log(start_prob)
        temp_end = -1.0 / math.log(end_prob)
        rate_of_temp = (temp_end / temp_start) ** (1.0 / (cycle_count - 1.0))

        selected_temp = temp_start
        delta_e_avg = 0.0
        number_of_accepted = 1
        prefix = "{}_{}_{}_".format(args.start_prob, args.end_prob, args.swap_prob)
        prefix = prefix.replace(".", "_")
        self.summary_file_name = summary_directory + prefix + "simulated_annealing.csv"
        create_dir(summary_directory)
        summary_file = FileWriter(self.summary_file_name)
        summary_file.write("iteration,energy_cost")
        summary_file.write([0, energy_cost])
        for i in range(cycle_count):
            s_print('Cycle: {} with Temperature: {}'.format(str(i), str(selected_temp)))
            nn_assignment = nearest_neighbour(assignment, swap_prob)
            nn_energy_cost = nn_assignment.total_energy_cost()
            delta_e = abs(nn_energy_cost - energy_cost)
            if nn_energy_cost > energy_cost:
                if i == 0:
                    delta_e_avg = delta_e
                denominator = (delta_e_avg * selected_temp)
                p = math.exp(-1 * math.inf) if denominator == 0 else math.exp(-delta_e / denominator)
                accept = True if random.random() < p else False
            else:
                accept = True
            # save current minimum to avoid losing details due to crash
            if self.min_cost > nn_energy_cost:
                self.min_assign = nn_assignment.copy()
                self.min_cost = nn_energy_cost
                nn_assignment.write("current_min")
                nn_assignment.write_bus_stat("current_min")

            if accept:
                assignment = nn_assignment
                energy_cost = nn_energy_cost
                summary_file.write([i, energy_cost])
                delta_e_avg = delta_e_avg + (delta_e - delta_e_avg) / number_of_accepted
                number_of_accepted += 1
            selected_temp = rate_of_temp * selected_temp
        summary_file.close()
        improve_perc = round(100.0 * (energy_cost - self.min_cost) / energy_cost, 3)
        s_print("Improvement in energy cost {}%".format(str(improve_perc)))
