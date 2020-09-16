from enum import Enum

from common.mode.AgencyMode import AgencyMode


class ServiceMode2019(Enum):
    WEEKDAY = '1'


def get_service_mode(day_code_str, agency_code_str):
    day_code_val = ServiceMode2019.WEEKDAY
    if day_code_str == "WEEKDAY":
        if agency_code_str == "DATA_2019":
            day_code_val = ServiceMode2019.WEEKDAY
    return day_code_val


default_agency_mode = AgencyMode.DATA_2019
default_service_id = ServiceMode2019.WEEKDAY

time_stamps = {}
selected_timestamp = 1597636800

time_stamps[ServiceMode2019.WEEKDAY] = selected_timestamp

range_values = {
    (AgencyMode.DATA_2019, ServiceMode2019.WEEKDAY): [0, 18],
}


def get_time_stamp(service_id):
    if service_id not in time_stamps.keys():
        return time_stamps[default_service_id]
    return time_stamps[service_id]


def get_range_values(agency_mode, service_id):
    if (agency_mode, service_id) not in range_values.keys():
        return range_values[(default_agency_mode, default_service_id)]
    return range_values[(agency_mode, service_id)]
