import math
import os
import random

from algo.common.types import AssignUtilConfig
from algo.greedy.GreedyBase import greedy_assign
from common.configs.global_constants import output_directory


class SimulatedAnnealing:
    def __init__(self, dump_structure, args):
        self.assignment = greedy_assign(dump_structure, AssignUtilConfig(do_print=True, do_shuffle=True), args=args)
        self.energy_cost = self.assignment.total_energy_cost()
        self.cycle_count = int(args.cycle_count)
        self.start_prob = float(args.start_prob)
        self.end_prob = float(args.end_prob)
        self.swap_prob = float(args.swap_prob)
        self.best_assigns = [self.assignment]
        self.best_costs = [self.energy_cost]
        self.anneal()

    def nearest_neighbour(self):
        """
        This corresponds to Algorithm 03
        Returns:
            nearest neighbor assignment
        """
        swap_count = max(1, int(self.swap_prob * len(self.assignment.get_trips())))
        child = None
        while swap_count > 0:
            child, swapped = self.assignment.swap()
            if swapped:
                swap_count -= 1
        if child is None:
            child = self.assignment
        return child

    def anneal(self):
        """
            This corresponds to Algorithm 03
        Returns:
            best solution after the end of the simulated annealing process
        """
        temp_start = -1.0 / math.log(self.start_prob)
        temp_end = -1.0 / math.log(self.end_prob)
        rate_of_temp = (temp_end / temp_start) ** (1.0 / (self.cycle_count - 1.0))

        selected_temp = temp_start
        delta_e_avg = 0.0

        summary_file = open(output_directory + "simulated_annealing_iterations.csv", "w+")
        summary_file.write("cycle_count,energy_cost\n")
        summary_file.flush()
        os.fsync(summary_file.fileno())
        for i in range(self.cycle_count):
            print('Cycle: ' + str(i) + ' with Temperature: ' + str(selected_temp))
            nn_assign = self.nearest_neighbour()
            cost_new = nn_assign.total_energy_cost()
            delta_e = abs(cost_new - self.energy_cost)
            if cost_new > self.energy_cost:
                if i == 0:
                    delta_e_avg = delta_e
                if (delta_e_avg * selected_temp) == 0:
                    p = math.exp(-math.inf)
                else:
                    p = math.exp(-delta_e / (delta_e_avg * selected_temp))
                accept = True if p > random.random() else False
            else:
                accept = True
            if accept:
                self.assignment = nn_assign
                self.energy_cost = cost_new
                summary_file.write("{},{}\n".format(str(i), str(self.energy_cost)))
                summary_file.flush()
                os.fsync(summary_file.fileno())
                delta_e_avg = delta_e_avg + (delta_e - delta_e_avg) / len(self.best_assigns)
                self.best_assigns.append(self.assignment.copy())
                self.best_costs.append(self.energy_cost)
            selected_temp = rate_of_temp * selected_temp
        summary_file.close()
        best_index = self.best_costs.index(min(self.best_costs))
        self.assignment = self.best_assigns[best_index]
