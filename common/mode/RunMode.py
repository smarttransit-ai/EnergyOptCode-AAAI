from enum import Enum

from common.parsers.ConfigParser import main_conf_parser

battery_capacity = main_conf_parser.get_float('CONSTANTS', 'battery_capacity')
pole_performance = main_conf_parser.get_float('CONSTANTS', 'pole_performance')

sample_route_min = main_conf_parser.get_int('SAMPLE_SPECS', 'sample_route_min')
sample_route_max = main_conf_parser.get_int('SAMPLE_SPECS', 'sample_route_max')
sample_route_incr = main_conf_parser.get_int('SAMPLE_SPECS', 'sample_route_incr')

sample_trip_min = main_conf_parser.get_int('SAMPLE_SPECS', 'sample_trip_min')
sample_trip_max = main_conf_parser.get_int('SAMPLE_SPECS', 'sample_trip_max')
sample_trip_incr = main_conf_parser.get_int('SAMPLE_SPECS', 'sample_trip_incr')

sample_slot_durations = main_conf_parser.literal_eval('SAMPLE_SPECS', 'sample_slot_durations')

sample_battery_capacity = main_conf_parser.get_float('SAMPLE_SPECS', 'battery_capacity')
sample_pole_performance = main_conf_parser.get_float('SAMPLE_SPECS', 'pole_performance')

full_route_count = main_conf_parser.get_int('FULL_SPECS', 'full_route_count')
full_trip_count = main_conf_parser.get_int('FULL_SPECS', 'full_trip_count')
full_slot_duration = main_conf_parser.get_int('FULL_SPECS', 'full_slot_duration')


class RunMode(Enum):
    FULL = 1
    SAMPLE = 2


def get_run_mode(run_mode_str):
    run_mode_val = RunMode.SAMPLE
    if run_mode_str == "FULL":
        run_mode_val = RunMode.FULL
    elif run_mode_str == "SAMPLE":
        run_mode_val = RunMode.SAMPLE
    return run_mode_val


rt_for_sample = []
for t in range(sample_trip_min, sample_trip_max + 1, sample_trip_incr):
    for r in range(sample_route_min, sample_route_max + 1, sample_route_incr):
        rt_for_sample.append((r, t))

rt_for_full = [(full_route_count, full_trip_count)]

default_run_mode = RunMode.SAMPLE

r_t_values = {
    RunMode.FULL: rt_for_full,
    RunMode.SAMPLE: rt_for_sample,
}

rth_for_sample = []
for t in range(sample_trip_min, sample_trip_max + 1, sample_trip_incr):
    for r in range(sample_route_min, sample_route_max + 1, sample_route_incr):
        for h in sample_slot_durations:
            rth_for_sample.append((r, t, h))

rth_for_full = [(full_route_count, full_trip_count, 1)]

r_t_h_values = {
    RunMode.FULL: rth_for_full,
    RunMode.SAMPLE: rth_for_sample,
}


def get_r_t_values(run_mode):
    if run_mode not in r_t_h_values.keys():
        result = r_t_values[default_run_mode]
    else:
        result = r_t_values[run_mode]
    return result


def get_r_t_h_values(run_mode):
    if run_mode not in r_t_h_values.keys():
        result = r_t_h_values[default_run_mode]
    else:
        result = r_t_h_values[run_mode]
    return result


# assumes SOC above 20% as safe zone
battery_safe_SOC = 0.8 * battery_capacity
sample_battery_safe_SOC = 0.8 * sample_battery_capacity

battery_capacities = {
    RunMode.FULL: battery_safe_SOC,
    RunMode.SAMPLE: sample_battery_safe_SOC,
}

pole_performances = {
    RunMode.FULL: pole_performance,
    RunMode.SAMPLE: sample_pole_performance,
}


def get_battery_capacity(run_mode):
    if run_mode not in battery_capacities.keys():
        return battery_capacities[default_run_mode]
    return battery_capacities[run_mode]


def get_pole_performance(run_mode):
    if run_mode not in pole_performances.keys():
        return pole_performances[default_run_mode]
    return pole_performances[run_mode]
