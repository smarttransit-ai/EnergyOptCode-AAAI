from enum import Enum


class AgencyMode(Enum):
    DATA_2019 = 'DATA_2019'


def get_agency_mode(agency_mode_str):
    agency_mode_val = AgencyMode.DATA_2019
    if agency_mode_str == "DATA_2019":
        agency_mode_val = AgencyMode.DATA_2019
    return agency_mode_val
