# -------------------------------------------------------------------------------- #
#                         FORCED UPDATE FOR ASSIGNMENT OBJECT                      #
# -------------------------------------------------------------------------------- #
from algo.common.types import AssignTypes, create_assignment
from base.entity.Charging import Charging
from base.entity.MovingTrip import create_mov_trip
from base.entity.OperatingTrip import OperatingTrip


class ForcedUpdateBase:
    def __init__(self, dump_structure, result_dir="", date="", args=None):
        self.assignment = create_assignment(AssignTypes.FORCE_UPDATE, dump_structure=dump_structure, args=args)
        self.result_dir = result_dir
        self.date = date
        self.missing_trips = []

    def force_update(self, _assignments_times=None, skip_reset=False):
        failed_count = 0
        if self.assignment.get_type() == AssignTypes.FORCE_UPDATE:
            if not skip_reset:
                self.assignment.reset()
            for _assign_pair_key in sorted(_assignments_times.keys()):
                for (_trip, _bus) in _assignments_times[_assign_pair_key]:
                    _info = self.assignment.add(_trip, _bus)
                    if _info.feasible():
                        if isinstance(_trip, OperatingTrip):
                            self.assignment.__dict__["_trip_alloc"].append(_trip)
                        if isinstance(_trip, Charging):
                            self.assignment.__dict__["_charging_alloc"].append(_trip)
                    else:
                        if isinstance(_trip, OperatingTrip):
                            self.missing_trips.append(_trip)
                        failed_count += 1
            print("Failed assignments {}".format(str(failed_count)))
        else:
            raise NotImplementedError
        return failed_count


class ForcedUpdate(ForcedUpdateBase):
    def force_update(self, _assignments_times=None, skip_reset=False, real_times=None, _skip_trips=None):
        import os
        if _skip_trips is None:
            _skip_trips = []
        failed_count = 0
        successful_assignments = open(self.result_dir + "successful.csv", "w+")
        conflict_assignments = open(self.result_dir + "conflict.csv", "w+")
        failed_assignments = open(self.result_dir + "failed.csv", "w+")
        trips_details = open(self.result_dir + "trip_counts.csv", "w+")

        route_trip_counts = {}
        successful_assignments.write("trip_id,bus_id,GTFS_start_time,GTFS_end_time,"
                                     "actual_start_time,actual_end_time,energy_consumed,energy_cost\n")

        conflict_assignments.write("date,bus_id,first_trip_id,first_trip_route_id,"
                                   "second_trip_id,second_trip_route_id,"
                                   "first_trip_GTFS_start_time,first_trip_GTFS_end_time,"
                                   "first_trip_actual_start_time,first_trip_actual_end_time,"
                                   "second_trip_GTFS_start_time,second_trip_GTFS_end_time,"
                                   "second_trip_actual_start_time,second_trip_actual_end_time,"
                                   "distance\n")

        failed_assignments.write("trip_id,bus_id,GTFS_start_time,GTFS_end_time,"
                                 "actual_start_time,actual_end_time\n")

        trips_details.write("route_id,number_of_trips,min_duration\n")

        if self.assignment.get_type() == AssignTypes.FORCE_UPDATE:
            if not skip_reset:
                self.assignment.reset()
            conflicting_trip_previous = []
            infecting_trip_previous = []
            route_min_duration = {}
            for _assign_pair_key in sorted(_assignments_times.keys()):
                for (_trip, _bus) in _assignments_times[_assign_pair_key]:
                    if _trip.get_trip_id() not in _skip_trips:
                        _info = self.assignment.add(_trip, _bus)
                        if _info.feasible():
                            if isinstance(_trip, OperatingTrip):
                                self.assignment.__dict__["_trip_alloc"].append(_trip)
                                route_id = _trip.route.route_id
                                duration_sec = _trip.get_duration().time_in_seconds
                                if route_id in route_min_duration.keys():
                                    min_duration = route_min_duration[route_id]
                                    if duration_sec < min_duration:
                                        route_min_duration[route_id] = duration_sec
                                else:
                                    route_min_duration[route_id] = duration_sec
                                count = 0
                                if _trip.route.route_id in route_trip_counts.keys():
                                    count = route_trip_counts[_trip.route.route_id]
                                count += 1
                                route_trip_counts[_trip.route.route_id] = count

                            if isinstance(_trip, Charging):
                                self.assignment.__dict__["_charging_alloc"].append(_trip)
                            if real_times is not None:
                                start, end = real_times[_trip.get_trip_id()]
                                successful_assignments.write(_trip.get_trip_id() + "," + _bus.bus_name + "," + \
                                                             _trip.start_time.time + "," + _trip.end_time.time + "," + \
                                                             start + "," + end + "," +
                                                             str(_trip.get_energy_consumed(_bus.bus_type)) + "," +
                                                             str(_trip.get_energy_cost(_bus.bus_type)) + "\n")

                        else:
                            allocations = self.assignment.list_bus_allocations(_bus)
                            start, end = real_times[_trip.get_trip_id()]
                            allocations = sorted(allocations, key=lambda _trip: _trip.start_s())
                            _prev_trip = allocations[-1]
                            if _prev_trip.get_trip_id() not in conflicting_trip_previous:
                                conflicting_trip_previous.append(_prev_trip.get_trip_id())
                            else:
                                infecting_trip_previous.append(_prev_trip.get_trip_id())
                            p_start, p_end = real_times[_prev_trip.get_trip_id()]
                            _mov_trip = create_mov_trip(_prev_trip, _trip)
                            data = [self.date, _bus.bus_name, _prev_trip.get_trip_id(), _prev_trip.route.route_id,
                                    _trip.get_trip_id(), _trip.route.route_id,
                                    _prev_trip.start_time.time, _prev_trip.end_time.time, p_start, p_end,
                                    _trip.start_time.time, _trip.end_time.time, start, end,
                                    str(_mov_trip.route.distance)]
                            conflict_assignments.write(",".join(data) + " \n")
                            failed_count += 1
                            if real_times is not None:
                                start, end = real_times[_trip.get_trip_id()]
                                failed_assignments.write(_trip.get_trip_id() + "," + _bus.bus_name + "," + \
                                                         _trip.start_time.time + "," + _trip.end_time.time + "," + \
                                                         start + "," + end + "\n")
            print("Failed assignments {}".format(str(failed_count)))
            failed_assignments.close()
            successful_assignments.close()
            if not failed_count:
                os.remove(self.result_dir + "failed.csv")
                os.remove(self.result_dir + "conflict.csv")
            if len(route_trip_counts) > 0:
                for route_id in route_trip_counts.keys():
                    trips_details.write("{},{},{}\n".format(str(route_id), str(route_trip_counts[route_id]),
                                                            str(route_min_duration[route_id])))
            return list(set(infecting_trip_previous))

        else:
            raise NotImplementedError
