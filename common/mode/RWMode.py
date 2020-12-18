from enum import Enum


class RWModeEnable(Enum):
    YES = 1,
    NO = 0


def get_rw_mode(rw_mode_str):
    rw_mode_val = RWModeEnable.NO
    if rw_mode_str == "YES":
        rw_mode_val = RWModeEnable.YES
    elif rw_mode_str == "NO":
        rw_mode_val = RWModeEnable.NO
    return rw_mode_val
