CODE DESCRIPTION:
algo - provides the code for greedy approach, simulated annealing and integer programming
base - provides the entities, models and utils which can be used to build up the algorithm
common - provides the constants and common utility shared among different folders (algo, base)
data - provides the input data.
execute - provides sample codes for executing our algorithms and comparing.
real - provides the real-world assignment data


DATA DESCRIPTION:
data/DATA_2019/1
    - these are just made into a dump, for quick access purpose while running algorithms.
    - gtfs_mini_dump.dat - contains a list of all operating trips, with energy estimates
    - move_trips_mini_dump.dat - contains energy estimates, distance and duration of all moving trips
data/DATA_2019/input/dump
    - these are just made into a dump, for quick access purpose while running algorithms.
    - shapes.dat - contains list of shape objects corresponding to the shapes.txt
    - stops.dat - contains list of stop objects corresponding to the stops.txt
    - stop_times.dat - contains list of stop_times objects corresponding to the stop_times.txt
    - trips.dat - contains list of trips objects corresponding to the trips.txt
real/trips/
    *.csv - these contains different real-word assignments
    and each csv file_contains following details
    tatripid,vid,start_pdist,end_pdist,num_docs,start_timestamp,end_timestamp,start_tmstmp,end_tmstmp,route_id

SAMPLE CODES:
There is two modes applications
    i) FULL
    ii) SAMPLE

Requirements:
    1.) python3.7
    2.) install all the contents in requirements.txt using "pip install requirements.txt"

In FULL MODE (make sure the config.ini "run_mode" value of "MODE" block is set with the value of "FULL")
1. to run greedy algorithm

python3 execute/greedy.py

2. to run simulated annealing algorithm

python3 execute/sim_anneal.py

3. to compare our algorithms with real-world assignments

python3 execute/compare.py

In SAMPLE MODE (make sure the config.ini "run_mode" value of "MODE" block is set with the value of "SAMPLE")
1. to run greedy algorithm

python3 execute/greedy.py

2. to run simulated annealing algorithm

python3 execute/sim_anneal.py

3. to run integer programming

python3 execute/int_prog.py

In both modes we can also add additional parameters to override the default values set for the arguments

For greedy algorithm and stimulated annealing algorithm
-weight_ev = weights of wait-time factor for electric buses (values: integers from 1 to 9)
-weight_gv = weights of wait-time factor for liquid-fuel buses (values: integers from 1 to 9)
-order_ev = order of wait-time factor for electric buses (any integers)
-order_gv = order of wait-time factor for liquid-fuel buses (any integers)

eg:-
python3 execute/greedy.py -weight_ev="3" -weight_gv="9" -order_ev="-3" -order_gv="-2"

this will run the greedy algorithm with wait-time factor of 0.003 for electric buses and wait-time factor of 0.09
for liquid-fuel buses.

For stimulated annealing algorithm only
-cycle_count = number of iterations in stimulated annealing algorithm
-start_prob = start probability
-end_prob = end probability
-swap_prob = swap probability

eg:-
python3 execute/sim_anneal.py -cycle_count="50000" -start_prob="0.5" -end_prob="0.01" -swap_prob="0.01"

this will run the simulated annealing algorithm for 50,000 iteration with start probability 0.5,
end probability 0.01 and swap probability 0.01