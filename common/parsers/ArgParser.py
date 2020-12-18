from argparse import ArgumentParser


class ConfigParserArgParser(ArgumentParser):
    def __init__(self):
        ArgumentParser.__init__(self)
        self.add_argument("-change_dict", help="Change dictionary", default={}, required=False)


class TuneArgParser(ArgumentParser):
    def __init__(self):
        ArgumentParser.__init__(self)
        self.add_argument("-start_limit_l", help="Start Limit (L)", default=1, required=False)
        self.add_argument("-end_limit_l", help="End Limit (L)", default=1, required=False)
        self.add_argument("-end_sub_limit_l", help="End Sub Limit (L)", default=1, required=False)
        self.add_argument("-swap_limit_l", help="Swap Limit (L)", default=1, required=False)
        self.add_argument("-start_limit_u", help="Start Limit (L)", default=9, required=False)
        self.add_argument("-end_limit_u", help="End Limit (L)", default=9, required=False)
        self.add_argument("-end_sub_limit_u", help="End Sub Limit (L)", default=9, required=False)
        self.add_argument("-swap_limit_u", help="Swap Limit (U)", default=5, required=False)


class WeightArgParserCommon(TuneArgParser):
    def __init__(self):
        TuneArgParser.__init__(self)
        self.add_argument("-weight_ev", help="Weight of waiting time for ev", default=0.0001, required=False)
        self.add_argument("-weight_gv", help="Weight of waiting time gv", default=0.002, required=False)


class ConfigParserCommon(WeightArgParserCommon):
    def __init__(self):
        WeightArgParserCommon.__init__(self)
        self.add_argument("-compute", help="Write  the computation to file", default=False, required=False)
        self.add_argument("-do_print", help="Print detailed results", default=False, required=False)
        self.add_argument("-dummy_assign", help="Allow the dummy assignments", default=True, required=False)
        self.add_argument("-suffix", help="custom summary suffix", default="", required=False)
        self.add_argument("-interface", help="Name of the additional interface", default="GAAction", required=False)
        self.add_argument("-time_limit", help="Maximum computation time", default=1, required=False)
        self.add_argument("-pop_limit", help="Number of Population", default=2, required=False)
        self.add_argument("-gen_limit", help="Number of Generation", default=1000, required=False)
        self.add_argument("-cycle_count", help="Number of Cycle", default=40000, required=False)
        self.add_argument("-sample_limit", help="Number of Samples", default=50, required=False)
        self.add_argument("-iteration_count", help="Number of Iterations", default=5000, required=False)
        self.add_argument("-start_prob", help="Starting Prob", default=0.2, required=False)
        self.add_argument("-end_prob", help="Starting Prob", default=0.09, required=False)
        self.add_argument("-swap_prob", help="Swapping Prob", default=0.05, required=False)


class CustomArgParser(ConfigParserCommon):
    def __init__(self):
        ConfigParserCommon.__init__(self)
        self.add_argument("-ev_count", help="Number of electric buses", default=3, required=False)
        self.add_argument("-gv_count", help="Number of gas buses", default=50, required=False)
        self.add_argument("-route_limit", help="Number of route in operations", default=17, required=False)
        self.add_argument("-trip_limit", help="Number of trips per route", default=230, required=False)


class CustomWTCArgParser(CustomArgParser):
    def __init__(self):
        CustomArgParser.__init__(self)
        self.add_argument("-slot_duration", help="Duration of slot in hours", default=1, required=False)
