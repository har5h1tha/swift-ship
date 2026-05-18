# order.py
# SwiftShip 
# Defines the Order class used across the entire project

import random

class Order:
    def __init__(self, order_id, weight, delivery_type, arrival_time):
        self.order_id     = order_id
        self.weight       = weight            # kg
        self.delivery_type = delivery_type    # "express" or "standard"
        self.arrival_time  = arrival_time     # minutes since warehouse opened
        self.burst_time    = round(weight * 0.5, 1)  # packing time in minutes
        self.start_time    = None             # filled by scheduler
        self.finish_time   = None             # filled by scheduler
        self.station       = None             # filled by scheduler

    def waiting_time(self):
        if self.start_time is None:
            return None
        return self.start_time - self.arrival_time

    def turnaround_time(self):
        if self.finish_time is None:
            return None
        return self.finish_time - self.arrival_time

    def priority_key(self):
        # express = 0 (higher priority), standard = 1
        type_rank = 0 if self.delivery_type == "express" else 1
        return (type_rank, self.weight)

    def __repr__(self):
        return (f"[{self.order_id} | {self.delivery_type.upper():<8} | "
                f"{self.weight:>5.1f}kg | arrival: t={self.arrival_time}min]")