import os

from common.mode.AgencyMode import get_agency_mode
from common.mode.RunMode import get_run_mode
from common.mode.ServiceMode import get_service_mode
from common.parsers.ConfigParser import main_conf_parser

agency_mode_key = main_conf_parser.get_str('MODE', 'agency_mode')
day_code_key = main_conf_parser.get_str('MODE', 'day_code')
run_mode_key = main_conf_parser.get_str('MODE', 'run_mode')

dummy_energy = main_conf_parser.get_float('CONSTANTS', 'dummy_energy')
dummy_cost = main_conf_parser.get_float('CONSTANTS', 'dummy_cost')
mile_to_meter = main_conf_parser.get_float('CONSTANTS', 'mile_to_m')
cost_of_electricity_per_kwh = main_conf_parser.get_float('CONSTANTS', 'electric_cost')
cost_of_gas_price_per_gallon = main_conf_parser.get_float('CONSTANTS', 'gas_cost')
default_slot_duration = main_conf_parser.get_float('CONSTANTS', 'default_slot_duration')
cp_locations = main_conf_parser.literal_eval('CONSTANTS', 'cp_locations')
default_dist_tol = main_conf_parser.get_float('CONSTANTS', 'default_dist_tol')
default_time_tol = main_conf_parser.get_float('CONSTANTS', 'default_time_tol')
max_ev_count = main_conf_parser.get_int('CONSTANTS', 'max_ev_count')
max_gv_count = main_conf_parser.get_int('CONSTANTS', 'max_gv_count')

agency_mode = get_agency_mode(agency_mode_key)
agency_mode_val = agency_mode.value
day_code = get_service_mode(day_code_key, agency_mode_key)
day_code_val = day_code.value
run_mode = get_run_mode(run_mode_key)
data_week_directory = "data/" + agency_mode_val + "/" + day_code_val + "/"

# FIXED DIRECTORIES
key_end = "E"
cur_dir = os.getcwd()
data_directory = cur_dir + "/data/"
result_directory = cur_dir + "/result/"
input_data_directory = data_directory + agency_mode_val + "/input/"
input_dump_directory = data_directory + agency_mode_val + "/input/dump/"
output_directory = result_directory + "output/"
dump_directory = result_directory + "dump/"
dump_log_directory = result_directory + "dump/log/"
dump_info_directory = result_directory + "dump/info/"
macosx_directory = result_directory + "__MACOSX"
summary_header_prefix = "no_of_bus_lines, no_of_trips, no_of_evs, no_of_icevs, slot_duration, "
trip_heading_prefix = "Trip ID, Trip, Start Time, End Time, Elec Energy, Gas Energy,"
charging_heading_prefix = "Charging ID, Pole, Start Time, End Time, "
bus_stat_heading = "Bus Name, Time(T), Count(T), Energy(T), Cost(T), " \
                   "Time(O), Count(O), Energy(O), Cost(O), " \
                   "Time(M), Count(M), Energy(M), Cost(M)," \
                   "Time(C), Count(C),"
