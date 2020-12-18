# -------------------------------------------------------------------------------- #
#                   SEPARATED BUILDING BLOCKS OF GENETIC ALGORITHM                 #
# -------------------------------------------------------------------------------- #
import random
from datetime import datetime

from algo.greedy.GreedyBase import greedy_assign
from base.entity.Bus import bus
from base.entity.OperatingTrip import OperatingTrip
from common.configs.model_constants import dummy_bus_type
from common.parsers.ConfigParser import main_conf_parser
from common.util.common_util import s_print

gen_alg_convergence_limit = main_conf_parser.get_int('GA', 'ga_converge_lmt')
mutation_break_time_limit = main_conf_parser.get_int('GA', 'mut_break_time_lmt')

min_pop = 1
mutation_prob = 0.005
min_mutation = 1
cross_over_ratio = 0.6
mutation_ratio = 0.005
selection_ratio = 1 - cross_over_ratio - mutation_ratio

dummy_bus_off_set = 2000


def score_population(population):
    """
    Args:
        population: list of assignments
    Returns:
        total energy costs of each of the assignment in the population
    """
    pop_scores = []
    for assignment in population:
        pop_scores.append(fitness(assignment))
    return pop_scores


def select(population, limit):
    """
    Args:
        population: list of assignments
        limit: number of assignment needs to be selected
    Returns:
        list first n assignments with lower energy costs, where n == limit
    """
    selected = []
    count = 0
    pop_scores = score_population(population)
    while count < max(min_pop, limit) and len(population) > 0:
        min_index = pop_scores.index(min(pop_scores))
        min_score = pop_scores[min_index]
        min_population = population[min_index]
        population.remove(min_population)
        pop_scores.remove(min_score)
        if min_population.complete:
            selected.append(min_population)
            count += 1
    return selected


def fitness(selected_assignment):
    """
    Args:
        selected_assignment: single assignment object of trips
    Returns:
        the fitness score of the selected population
    """
    return selected_assignment.total_energy_cost()


def assign(dump_structure, assign_util_config, arg):
    """
    Args:
        dump_structure: contains the trips, buses and charging
        assign_util_config: configuration for doing assigning
        arg: additional arguments, eg: weights for waiting time
    Returns:
        assignment of buses to the transit trips
    """
    return greedy_assign(dump_structure, assign_util_config, args=arg)


def mutate(next_population_parents):
    """
    Args:
        next_population_parents: next generation parents
    Returns:
        mutated child assignment
    """
    parent = random.choice(next_population_parents.copy())
    mutation_count = max(min_mutation, int(mutation_prob * len(parent.get_trips())))
    at_least_one_mutated = False
    start_time = datetime.now()
    parent_cpy = parent.copy()
    child = None
    while mutation_count > 0:
        if (datetime.now() - start_time).total_seconds() > mutation_break_time_limit:
            if not at_least_one_mutated:
                s_print("Nothing mutated breaking due to time limitation")
            break
        child, mutated = parent_cpy.mutate()
        if mutated:
            at_least_one_mutated = True
            mutation_count -= 1
            parent_cpy = child.copy()
        else:
            parent_cpy = parent.copy()

    if child is None:
        child = parent.copy()
    return child.copy()


def __crossover(initial, remaining):
    """
    Args:
        initial: initial portion of an assignment
        remaining: remaining portion of an assignment
    Returns:
        combined assignment of initial and remaining
    """
    dummy_count = 0
    for selected_trip in remaining.get_trips():
        selected_bus = remaining.get(selected_trip)
        if selected_bus is None:
            raise ValueError
        if isinstance(selected_trip, OperatingTrip):
            feasible = initial.assign(selected_trip, selected_bus)
            if not feasible:
                initial.assign(selected_trip, bus(str(dummy_bus_off_set + dummy_count), dummy_bus_type))
    return initial


def crossover(next_population_parents):
    """
    Args:
        next_population_parents: next generation parents
    Returns:
        list of 2 best crossover based on two crossover and next generation parents
    """
    parent_1 = random.choice(next_population_parents.copy())
    parent_2 = random.choice(next_population_parents.copy())
    cross_over_1, cross_over_1_remain = parent_1.crossover_init()
    cross_over_2, cross_over_2_remain = parent_2.crossover_init()
    cross_over_1 = __crossover(cross_over_1, cross_over_2_remain)
    cross_over_2 = __crossover(cross_over_2, cross_over_1_remain)
    new_population = [parent_1, parent_2, cross_over_1, cross_over_2]
    return select(new_population, 2)


def create_population_thread(process_name, populations, dump_structure, assign_util_config, arg):
    while True:
        assignment = assign(dump_structure, assign_util_config, arg)
        assign_type = assignment.get_type()
        if assignment is not None:
            if not (populations.append(assignment)):
                break
            s_print("{} assigned with energy cost ${} using Algorithm {}".
                    format(process_name, assignment.total_energy_cost(), str(assign_type)))


def create_mutation_thread(process_name, mutations, next_generation_parents):
    while True:
        mutation = mutate(next_generation_parents)
        if not (mutations.append(mutation)):
            break
        s_print("{} mutated with energy cost ${}".
                format(process_name, mutation.total_energy_cost()))


def create_crossover_thread(process_name, cross_overs, next_generation_parents):
    while True:
        cross_over_set = crossover(next_generation_parents)
        if not (cross_overs.append(cross_over_set[0])):
            break
        s_print("{} crossover with energy cost ${}".
                format(process_name, cross_over_set[0].total_energy_cost()))
        if not (cross_overs.append(cross_over_set[1])):
            break
        s_print("{} crossover with energy cost ${}".
                format(process_name, cross_over_set[1].total_energy_cost()))
