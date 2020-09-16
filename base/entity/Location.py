from common.configs.global_constants import run_mode
from common.configs.model_constants import route_location_type, charging_location_type
# this is used to identify particular location
# this contains the latitude , longitude and stop identifier
# and other details received from GTFS data set
from common.mode.RunMode import get_pole_performance


class Location(object):
    def __init__(self, stop, location_type):
        self.lat = stop.stop_lat
        self.lon = stop.stop_lon
        self.id = stop.stop_id
        self.location_name = stop.stop_name
        self.location_type = location_type

    def lat_lon(self, deliminator=","):
        return str(round(float(self.lat), 5)) + deliminator + str(round(float(self.lon), 5))

    def __str__(self):
        return self.location_name

    def __key__(self):
        location_name = self.location_name.replace("\"", "")
        return location_name.replace("\'", "")


class RoutePoint(Location):
    def __init__(self, stop):
        super(RoutePoint, self).__init__(stop, route_location_type)


class ChargingPoint(Location):
    def __init__(self, stop):
        super(ChargingPoint, self).__init__(stop, charging_location_type)
        self.performance = get_pole_performance(run_mode)
