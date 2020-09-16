from base.entity.Charging import Charging
from base.entity.MovingTrip import MovingTrip
from base.entity.OperatingTrip import OperatingTrip
from common.Time import add


class InvalidMovementException(Exception):
    def __init__(self, *args):
        super(InvalidMovementException, self).__init__(args)


# this used for temporary saving moving of buses from one place to another
class BusMovement(object):
    def __init__(self, selected_bus, trip, movement_type):
        self.selected_bus = selected_bus
        self.trip = trip
        self.movement_type = movement_type

    def __str__(self):
        if isinstance(self.trip, (MovingTrip, OperatingTrip, Charging)):
            _duration = self.trip.get_duration()
            end_time = add(self.trip.start_time, _duration)
            format_string = self.trip.start_time.time + "-" + end_time.time + " | " + self.trip.__str__()
        else:
            raise InvalidMovementException("Invalid movement type {}".format(type(self.trip).__name__))
        return format_string
