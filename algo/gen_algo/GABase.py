import math
import multiprocessing
from datetime import datetime

from algo.common.types import AssignUtilConfig
from algo.gen_algo.commons import min_pop, mutation_ratio, cross_over_ratio, \
    mutate, crossover, min_mutation, create_population_thread, create_crossover_thread, create_mutation_thread, \
    gen_alg_convergence_limit, assign, select, selection_ratio
from algo.gen_algo.commons import score_population, fitness
from base.model.Assignment import Assignment
from common.CustomMP import CMPSystem, process_count
from common.Time import time
from common.configs.global_constants import summary_directory
from common.util.common_util import s_print, create_dir
from common.writer.FileWriter import FileWriter


class GABase(object):
    def __init__(self, arg, dump_structure):
        self.prefix = str(int(arg.ev_count)) + "_" + str(int(arg.gv_count)) + "_" + str(int(arg.route_limit)) + \
                      "_" + str(int(arg.trip_limit)) + "_"
        self.population_limit = int(arg.pop_limit)
        self.generation_limit = int(arg.gen_limit)
        self.dump_structure = dump_structure
        self.assign_util_config = AssignUtilConfig(
            compute=bool(arg.compute),
            do_print=bool(arg.do_print),
            dummy_assign=bool(arg.dummy_assign),
            time_limit=int(arg.time_limit)
        )
        self.sys_population = []
        self.best_costs = []
        self.over_all_best = None
        self.generation_count = 0
        self.time_consumed = 0
        self.summary_file_name = ""
        self.run(arg)

    def run(self, arg):
        start_time = datetime.now()
        self._init_population(arg)
        convergence_limit = 0
        minimum_cost = math.inf
        new_population = self.sys_population
        generation = 0
        self.summary_file_name = summary_directory + "genetic_algorithm.csv"
        create_dir(summary_directory)
        summary_file = FileWriter(self.summary_file_name)
        summary_file.write("iteration,energy_cost")
        while convergence_limit < gen_alg_convergence_limit and generation < self.generation_limit:
            s_print("Current Generation {}".format(str(generation)))
            scores = score_population(new_population)
            best = new_population[scores.index(min(scores))]
            fitness_cost = fitness(best)
            self.best_costs.append(fitness_cost)
            if fitness_cost < minimum_cost:
                convergence_limit = 0
                minimum_cost = fitness_cost
                self.over_all_best = best
            else:
                convergence_limit += 1
            summary_file.write([generation, minimum_cost])
            new_population = select(new_population, max(int(len(new_population) * selection_ratio), min_pop))
            s_print("Creating next generation ")
            new_population.extend(self._create_crossover(new_population))
            new_population.extend(self._create_mutation(new_population))
            self.population_limit = len(new_population)
            self.generation_count = generation
            generation += 1
        summary_file.close()
        end_time = datetime.now()
        self.time_consumed = (end_time - start_time).total_seconds()
        s_print("Total time taken is " + time(int(self.time_consumed)).time)
        if self.over_all_best is not None:
            if isinstance(self.over_all_best, Assignment):
                self.over_all_best.write(self.dump_structure.__key__())
                self.over_all_best.write_bus_stat(self.dump_structure.__key__(), do_print=True)

    def _init_population(self, arg):
        raise NotImplementedError

    def _create_crossover(self, next_generation_parents):
        raise NotImplementedError

    def _create_mutation(self, next_generation_parents):
        raise NotImplementedError


class SerialGA(GABase):
    def _init_population(self, arg):
        for population_id in range(max(min_pop, self.population_limit)):
            assignment = assign(self.dump_structure, self.assign_util_config, arg)
            if assignment is not None:
                self.sys_population.append(assignment)

    def _create_mutation(self, next_population_parents):
        mutations = []
        s_print("Adding mutations --- STARTED")
        while len(mutations) < self.population_limit * mutation_ratio:
            mutations.append(mutate(next_population_parents))
        s_print("Adding mutations --- FINISHED")
        return mutations

    def _create_crossover(self, next_population_parents):
        crossovers = []
        s_print("Adding crossovers --- STARTED")
        while len(crossovers) < self.population_limit * cross_over_ratio:
            crossovers.extend(crossover(next_population_parents))
        s_print("Adding crossovers --- FINISHED")
        return crossovers


class ParallelGA(GABase):
    def _init_population(self, arg):
        cmp_sys = CMPSystem(self.population_limit)
        cmp_sys.add_proc(func=create_population_thread,
                         args=(self.dump_structure, self.assign_util_config, arg))
        self.sys_population = cmp_sys.run()

    def _create_mutation(self, next_population_parents):
        mutation_count = max(int(self.population_limit * mutation_ratio), min_mutation)
        cmp_sys = CMPSystem(mutation_count)
        cmp_sys.add_proc(func=create_mutation_thread, args=(next_population_parents,))
        return cmp_sys.run()

    def _create_crossover(self, next_population_parents):
        crossover_count = int(self.population_limit * cross_over_ratio)
        cmp_sys = CMPSystem(crossover_count)
        cmp_sys.add_proc(func=create_crossover_thread, args=(next_population_parents,))
        return cmp_sys.run()


class ParallelGAV2(GABase):
    def _init_population(self, arg):
        process_pool = multiprocessing.Pool(process_count)
        data = []
        for i in range(self.population_limit + 1):
            data.append([self.dump_structure, self.assign_util_config, arg])
        self.sys_population = process_pool.starmap(assign, data, arg)

    def _create_mutation(self, next_population_parents):
        mutation_count = max(int(self.population_limit * mutation_ratio), min_mutation)
        process_pool = multiprocessing.Pool(process_count)
        data = []
        for i in range(mutation_count + 1):
            data.append([next_population_parents])
        return process_pool.starmap(mutate, data)

    def _create_crossover(self, next_population_parents):
        crossover_count = int(self.population_limit * cross_over_ratio)
        process_pool = multiprocessing.Pool(process_count)
        data = []
        for i in range(crossover_count + 1):
            data.append([next_population_parents])
        return process_pool.starmap(crossover, data)
