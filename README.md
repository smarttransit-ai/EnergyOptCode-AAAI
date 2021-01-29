# ABOUT

This repository describes the results of the code and the data for the following paper - https://smarttransit.ai/files/aaai21.pdf. 

### ABSTRACT 

*Affordable public transit services are crucial for communities since they enable residents to access employment, education, and other services. Unfortunately, transit services that provide wide coverage tend to suffer from relatively low utilization, which results in high fuel usage per passenger per mile, leading to high operating costs and environmental impact. Electric vehicles (EVs) can reduce energy costs and environmental impact, but most public transit agencies have to employ them in combination with conventional, internal-combustion engine vehicles due to the high upfront costs of EVs. To make the best use of such a mixed fleet of vehicles, transit agencies need to optimize route assignments and charging schedules, which presents a challenging problem for large transit networks. We introduce a novel problem formulation to minimize fuel and electricity use by assigning vehicles to transit trips and scheduling them for charging, while serving an existing fixed-route transit schedule. We present an integer program for optimal assignment and scheduling, and we propose polynomial-time heuristic and meta-heuristic algorithms for larger networks. We evaluate our algorithms on the public transit service of Chattanooga, TN using operational data collected from transit vehicles. Our results show that the proposed algorithms are scalable and can reduce energy use and, hence, environmental impact and operational costs. For Chattanooga, the proposed algorithms can save $145,635 in energy costs and 576.7 metric tons of CO2 emission annually.*

### ACKNOWLEDGEMENT

This material is based upon work supported by the Department of Energy, Office of Energy Efficiency and Renewable Energy (EERE), under Award Number DE-EE0008467. 

**Disclaimer**: This report was prepared as an account of work sponsored by an agency of the United States Government. Neither the United States Government nor any agency thereof, nor any of their employees, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness of any information, appa- ratus, product, or process disclosed, or represents that its use would not infringe privately owned rights.

### DIRECTORIES

[algo](algo): Python source code for greedy approach, simulated annealing, genetic algorithm, and integer programming

[base](base): source code for entities, models, and utilities that are used to implement the algorithms

[common](common): constants and common utilities shared by source files in other folders ([algo](algo), [base](base))

[execute](execute): sample Python source codes for executing our algorithms and experiments

[data](data): input data for assignment problem


### DATA DESCRIPTION

[data/DATA_2019/1](data/DATA_2019/1)
   
- these are just made into a dump, for quick access purpose while running algorithms.
- [gtfs_mini_dump.dat](data/DATA_2019/1/gtfs_mini_dump.dat): list of all transit trips, with energy estimates
- [move_trips_mini_dump.dat](data/DATA_2019/1/move_trips_mini_dump.dat): energy estimates, distance and duration of all non-service trips

[data/DATA_2019/input/dump](data/DATA_2019/input/dump)

- this is just made into a dump, for quick access purpose while running algorithms.
- [stops.dat](data/DATA_2019/input/dump/stops.dat): list of stop objects corresponding to the ```stops.txt```

[data/DATA_2019/trips](data/DATA_2019/trips)

- *.csv: real-word assignments (recorded from the transit agency)
- each CSV file_contains following fields:

```entry_no```, ```trip_id```, ```vehicle_id```, ```start_pdist```, ```end_pdist```, ```num_docs```, ```start_timestamp```, ```end_timestamp```, ```start_tmstmp```, ```end_tmstmp```, ```route_id```


### SAMPLE SOURCE CODES

Algorithms can be executed in one of two modes:

1. ```FULL```: assignment for full transit schedule, enabling comparison with existing real-world assignments
2. ```SAMPLE```: assignment for sample set of trips, enabling comparison with integer programming

#### Requirements
1. Python 3.7
2. Install all modules listed in [requirements.txt](requirements.txt) (using the command ```pip install requirements.txt```).


#### FULL MODE
Make sure that in [config.ini](config.ini), the value of ```run_mode``` in the block ```MODE``` is set to ```FULL```.

1. run greedy algorithm

```shell
python3 execute/greedy.py
```
2. run simulated annealing algorithm

```shell
python3 execute/sim_anneal.py
```

3. compare our algorithms with real-world assignments

```shell
python3 execute/compare.py
```

4. run genetic algorithm

```shell
python3 execute/gen_algo.py
```

#### SAMPLE MODE
Make sure that in [config.ini](config.ini), the value of ```run_mode``` in the block ```MODE``` is set to ```SAMPLE```.

1. run greedy algorithm

```shell
python3 execute/greedy.py
```

2. run simulated annealing algorithm

```shell
python3 execute/sim_anneal.py
```

3. run integer programming

```shell
python3 execute/int_prog.py
```

4. run genetic algorithm

```shell
python3 execute/gen_algo.py
```

#### CUSTOMIZING PARAMETERS
In both modes, we can also add additional parameters to override the default argument values.
For greedy algorithm and simulated annealing algorithm:

```-weight_ev``` = wait-time factor for electric buses

```-weight_gv``` = wait-time factor for liquid-fuel buses

***Example:***
```shell
python3 execute/greedy.py -weight_ev="0.003" -weight_gv="0.09"
```

This will run the greedy algorithm with wait-time factor of 0.003 for electric buses and wait-time factor of 0.09 for liquid-fuel buses.

For simulated annealing algorithm only:

```-cycle_count``` = number of iterations in simulated annealing algorithm

```-start_prob``` = start probability

```-end_prob``` = end probability

```-swap_prob``` = swap probability

***Example:***
```shell
python3 execute/sim_anneal.py -cycle_count="50000" -start_prob="0.5" -end_prob="0.01" -swap_prob="0.01"
```

This will run the simulated annealing algorithm for 50,000 iteration with start probability 0.5, end probability 0.01, and swap probability 0.01.
