from datetime import datetime

from common.configs.global_constants import image_directory, summary_directory
from common.util.common_util import create_dir, s_print


def nearest_neighbour(assignment, swap_prob):
    """
    Returns:
        nearest neighbor assignment
    """
    swap_count = max(1, int(swap_prob * len(assignment.get_trips())))
    at_least_one_swapped = False
    start_time = datetime.now()
    child = None
    while swap_count > 0:
        if (datetime.now() - start_time).total_seconds() > 4:
            if not at_least_one_swapped:
                s_print("Nothing modified breaking due to time limitation")
            break
        child, swapped = assignment.swap()
        if swapped:
            at_least_one_swapped = True
            swap_count -= 1

    if child is None:
        child = assignment
    return child


def plot(obj):
    import pandas as pd
    import matplotlib.pyplot as plt
    df = pd.read_csv(obj.summary_file_name)
    plt.figure()
    df.plot(x="iteration", y="energy_cost")
    plt.xlabel("Iterations")
    plt.ylabel("Energy Cost")
    image_file_name = obj.summary_file_name.replace(".csv", ".png")
    create_dir(image_directory)
    image_file_name = image_file_name.replace(summary_directory, image_directory)
    plt.savefig(image_file_name)
