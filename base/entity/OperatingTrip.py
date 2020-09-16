from base.entity.Location import RoutePoint
from base.entity.Trip import Trip
from common.Time import diff

# main class used to denote the operating trips
from common.configs.global_constants import key_end


class OperatingTrip(Trip):
    def __init__(self, bus_trip):
        super(OperatingTrip, self).__init__(RoutePoint(bus_trip.start_pos), RoutePoint(bus_trip.end_pos))
        self.start_time = bus_trip.start_time
        self.end_time = bus_trip.end_time
        self.duration = diff(self.end_time, self.start_time)
        self.route_name = bus_trip.trip_headsign
        self.direction = bus_trip.direction_id
        self.trip_id = bus_trip.trip_id
        self.route.add_route_id(bus_trip.route_id)

    def get_trip_id(self, data_type=str):
        """
        Returns:
            returns the trip_id without last three digits from GTFS dataset
            to map with trip_level_data
        """
        return data_type(self.trip_id[:-3])

    def add_stops(self, stops):
        self.route.add_stops(stops)

    def get_duration(self):
        return self.duration

    def __str__(self):
        format_string = "OPR_TRIP | " + self.route.route_id + "(" + self.direction + ") " + \
                        self.route.__str__()
        return format_string.replace("\"", "\'")

    def __key__(self):
        return "O" + str(self.trip_id) + key_end
