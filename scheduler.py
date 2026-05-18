        
import copy

# ─────────────────────────────────────────────
#  STATION CLASS (Mallika)
# ─────────────────────────────────────────────

class Station:
    def __init__(self, station_id):
        self.station_id   = station_id
        self.orders       = []     # orders assigned to this station
        self.busy_until   = 0      # minute the station is free next
        self.is_active    = True   # False if station breaks down

    def assign(self, order, current_time):
        start            = max(self.busy_until, order.arrival_time)
        order.start_time = start
        order.finish_time = start + order.burst_time
        order.station    = self.station_id
        self.busy_until  = order.finish_time
        self.orders.append(order)

    def total_load(self):
        return sum(o.burst_time for o in self.orders)

    def __repr__(self):
        return f"Station-{self.station_id} (load={self.total_load():.1f}min)"


def make_stations(n=3):
    return [Station(i + 1) for i in range(n)]


# ─────────────────────────────────────────────
#  FCFS — First Come First Served (Mallika)
# ─────────────────────────────────────────────

def fcfs(orders, num_stations=3):
    """
    OS Concept: FCFS CPU Scheduling
    Orders processed in order of arrival_time.
    Each order goes to the station that is free soonest.
    No priority — fairness over speed.
    """
    stations = make_stations(num_stations)
    # Sort by arrival time (FCFS rule)
    queue = sorted(copy.deepcopy(orders), key=lambda o: o.arrival_time)

    for order in queue:
        # Pick station free earliest
        station = min(stations, key=lambda s: s.busy_until)
        station.assign(order, station.busy_until)

    return stations


