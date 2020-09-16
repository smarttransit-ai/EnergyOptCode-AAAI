DIRECTORIES:
algo: Python source code for greedy approach, simulated annealing, and integer programming
base: source code for entities, models, and utilities that are used to implement the algorithms
common: constants and common utilities shared by source files in other folders (algo, base)
execute: sample Python source codes for executing our algorithms and experiments
data: input data for assignment problem
real: data about existing real-world assignments


DATA DESCRIPTION:
data/DATA_2019/1
    - these are just made into a dump, for quick access purpose while running algorithms.
    - gtfs_mini_dump.dat: list of all transit trips, with energy estimates
    - move_trips_mini_dump.dat: energy estimates, distance and duration of all non-service trips
data/DATA_2019/input/dump
    - this is just made into a dump, for quick access purpose while running algorithms.
    - stops.dat: list of stop objects corresponding to the stops.txt
real/trips/
    *.csv: real-word assignments (recorded from the transit agency)
    each CSV file_contains following fields:
    entry_no, trip_id, vehicle_id, start_pdist, end_pdist, num_docs, start_timestamp, end_timestamp, start_tmstmp, end_tmstmp, route_id


SAMPLE SOURCE CODES:
Algorithms can be executed in one of two modes:
    i) FULL: assignment for full transit schedule, enabling comparison with existing real-world assignments
    ii) SAMPLE: assignment for sample set of trips, enabling comparison with integer programming

Requirements:
    1.) Python 3.7
    2.) install all modules listed in requirements.txt using "pip install requirements.txt"


In FULL MODE (make sure that config.ini "run_mode" value of "MODE" block is set to "FULL"):

1. run greedy algorithm

python3 execute/greedy.py

2. run simulated annealing algorithm

python3 execute/sim_anneal.py

3. compare our algorithms with real-world assignments

python3 execute/compare.py

In SAMPLE MODE (make sure that config.ini "run_mode" value of "MODE" block is set to "SAMPLE")

1. run greedy algorithm

python3 execute/greedy.py

2. run simulated annealing algorithm

python3 execute/sim_anneal.py

3. run integer programming

python3 execute/int_prog.py


In both modes, we can also add additional parameters to override the default argument values.
For greedy algorithm and simulated annealing algorithm:
-weight_ev = wait-time factor for electric buses
-weight_gv = wait-time factor for liquid-fuel buses

Example:
python3 execute/greedy.py -weight_ev="0.003" -weight_gv="0.09"
This will run the greedy algorithm with wait-time factor of 0.003 for electric buses and wait-time factor of 0.09 for liquid-fuel buses.

For simulated annealing algorithm only:
-cycle_count = number of iterations in simulated annealing algorithm
-start_prob = start probability
-end_prob = end probability
-swap_prob = swap probability

Example:
python3 execute/sim_anneal.py -cycle_count="50000" -start_prob="0.5" -end_prob="0.01" -swap_prob="0.01"
This will run the simulated annealing algorithm for 50,000 iteration with start probability 0.5, end probability 0.01, and swap probability 0.01.
