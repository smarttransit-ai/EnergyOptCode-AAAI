from enum import Enum


class ChargeModeEnable(Enum):
    YES = 1,
    NO = 0


def get_charge_mode(charge_mode_str):
    charge_mode_val = ChargeModeEnable.YES
    if charge_mode_str == "YES":
        charge_mode_val = ChargeModeEnable.YES
    elif charge_mode_str == "NO":
        charge_mode_val = ChargeModeEnable.NO
    return charge_mode_val
