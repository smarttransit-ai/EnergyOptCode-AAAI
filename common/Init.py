import ast
import os
import sys

sys.path.append(os.getcwd())
from common.parsers.ArgParser import ConfigParserArgParser
from common.parsers.ConfigParser import CustomConfigParserBase, CONFIG_FILE

config = CustomConfigParserBase(CONFIG_FILE, "w+")
MODE_block = {
    "agency_mode": "DATA_2019",
    "run_mode": "FULL",
    "day_code": "WEEKDAY",
    "enable_charging": "YES",
    "enable_real_world": "NO",
}
config.set_block("MODE", MODE_block)

CONSTANTS_block = {
    "dummy_energy": 100000,
    "dummy_cost": 100000,
    "mile_to_m": 1609.34,
    "electric_cost": 0.09602,
    "gas_cost": 2.05,
    "co2_emission_per_kwh": 0.707,
    "co2_emission_per_gallon": 8.887,
    "battery_capacity": 270,
    "pole_performance": 65,
    "default_slot_duration": 1,
    "cp_locations": ["143", "400", "690"],
    "default_dist_tol": 150,
    "default_time_tol": 0.1,
    "max_ev_count": 3,
    "max_gv_count": 50,
    "selected_date": "3/2/2020",
    "random_seed": 0
}
config.set_block("CONSTANTS", CONSTANTS_block)

SAMPLE_SPECS_block = {
    "sample_route_min": 1,
    "sample_route_max": 12,
    "sample_route_incr": 1,
    "sample_trip_min": 10,
    "sample_trip_max": 10,
    "sample_trip_incr": 10,
    "battery_capacity": 54,
    "pole_performance": 13,
    "sample_slot_durations": [1.0],
}
config.set_block("SAMPLE_SPECS", SAMPLE_SPECS_block)

FULL_SPECS_block = {
    "full_route_count": 17,
    "full_trip_count": 230,
    "full_slot_duration": 1,
}
config.set_block("FULL_SPECS", FULL_SPECS_block)

GA_block = {
    "ga_converge_lmt": 100,
    "mut_break_time_lmt": 4
}
config.set_block("GA", GA_block)

IP_block = {
    "sabine_dir": "/project/laszka/Amu",
    "rnslab_dir": "/home/asivagna",
    "local_dir": "/Users/amutheezansivagnanam",
    "time_limit": -1
}
config.set_block("IP", IP_block)

try:
    arg_parser = ConfigParserArgParser()
    args = arg_parser.parse_args()
    change_dicts = args.change_dict
    change_dicts = ast.literal_eval(change_dicts)
    for key in change_dicts.keys():
        config.set_value(key, change_dicts[key])
except ValueError:
    pass
config.write_conf()
