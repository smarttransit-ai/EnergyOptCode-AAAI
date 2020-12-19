days = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
    21: "twentyone",
    22: "twentytwo",
    23: "twentythree",
    24: "twentyfour",
    25: "twentyfive",
    26: "twentysix",
    27: "twentyseven",
    28: "twentyeight",
    29: "twentynine",
    30: "thirty",
    31: "thirtyone"
}

days_rev = {}
for key in days.keys():
    val = days[key]
    days_rev[val] = key

months = {
    2: "feb",
    3: "mar",
    4: "apr",
}

months_rev = {}
for key in months.keys():
    val = months[key]
    months_rev[val] = key


def convert_month_day_num_to_str(date_str):
    month, day = date_str.split("/")
    month_val = months[int(month)]
    day_val = days[int(day)]
    return month_val, day_val
