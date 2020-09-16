from argparse import ArgumentParser


class ParameterConfigArgParser(ArgumentParser):
    def __init__(self):
        """
            This sets default parameters for running all algorithms,
            we can change this by changing the values at here or
            in run time by providing arguments
            eg : execute/sim_anneal.py -start_prob="0.9"
        """
        ArgumentParser.__init__(self)
        self.add_argument("-weight_ev", help="Weight of waiting time for ev", default=3, required=False)
        self.add_argument("-weight_gv", help="Weight of waiting time gv", default=9, required=False)
        self.add_argument("-order_ev", help="Order of weight for ev", default=-3, required=False)
        self.add_argument("-order_gv", help="Order of weight for gv", default=-2, required=False)
        self.add_argument("-cycle_count", help="Number of Cycle", default=50000, required=False)
        self.add_argument("-start_prob", help="Starting Prob", default=0.5, required=False)
        self.add_argument("-end_prob", help="Starting Prob", default=0.01, required=False)
        self.add_argument("-swap_prob", help="Swapping Prob", default=0.01, required=False)


class ConfigParser(ParameterConfigArgParser):
    def __init__(self):
        """
            These are configuration, just for writing the results and statistics
            and some minor changes in the implementation
            -dummy_assign - if this enabled it will allow to assign dummy buses, in case the algorithms
            unable to assign the all the trips with the provided buses
        """
        ParameterConfigArgParser.__init__(self)
        self.add_argument("-compute", help="Write  the computation to file", default=False, required=False)
        self.add_argument("-do_print", help="Print detailed results", default=False, required=False)
        self.add_argument("-dummy_assign", help="Allow the dummy assignments", default=True, required=False)


class CustomArgParser(ConfigParser):
    def __init__(self):
        """
            This provides basic setting
        """
        ConfigParser.__init__(self)
        self.add_argument("-ev_count", help="Number of electric buses", default=3, required=False)
        self.add_argument("-gv_count", help="Number of gas buses", default=50, required=False)
        self.add_argument("-route_limit", help="Number of route in operations", default=17, required=False)
        self.add_argument("-trip_limit", help="Number of trips per route", default=230, required=False)


class CustomWTCArgParser(CustomArgParser):
    def __init__(self):
        """
            This provides an additional setting of slot_duration, which specifies the charging duration
        """
        CustomArgParser.__init__(self)
        self.add_argument("-slot_duration", help="Duration of slot in hours", default=1, required=False)
