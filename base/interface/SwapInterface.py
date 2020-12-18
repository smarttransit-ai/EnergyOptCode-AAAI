import random as rand

from base.entity.OperatingTrip import OperatingTrip
from base.model.AssignBase import GenericInterface


class SwapInterface(GenericInterface):
    def _inner_swap(self, child, selected_bus_a, selected_bus_b):
        swapped = False
        if selected_bus_a != selected_bus_b:
            allocation_bus_a = child.list_bus_allocations(selected_bus_a)
            allocation_bus_b = child.list_bus_allocations(selected_bus_b)
            if len(allocation_bus_a) > 0 and len(allocation_bus_b) > 0:
                all_allocation = allocation_bus_a.copy() + allocation_bus_b.copy()
                all_allocation = sorted(all_allocation, key=lambda trip: trip.start_s())
                mid_point = int(len(all_allocation) / 2)
                first_half = all_allocation[:mid_point]
                second_half = all_allocation[mid_point:]
                success = False
                choose_alloc = rand.choice([first_half, second_half])
                for alloc in choose_alloc:
                    success = child.remove(alloc)
                    if not success:
                        break
                if success:
                    success = False
                    for alloc in choose_alloc:
                        if isinstance(alloc, OperatingTrip):
                            if alloc in allocation_bus_a:
                                success = child.assign(alloc, selected_bus_b)
                            elif alloc in allocation_bus_b:
                                success = child.assign(alloc, selected_bus_a)
                            if not success:
                                break
                if not success:
                    child = self.copy()
                else:
                    swapped = True
            else:
                child = self.copy()
        return child, swapped

    def base_copy(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def get_trips(self):
        raise NotImplementedError

    def add(self, key, val):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError
