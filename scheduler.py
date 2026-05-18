# scheduler.py
# SwiftShip 
# FCFS, SJF, Hybrid Scheduler, Station Breakdown

import copy

# ─────────────────────────────────────────────
#  STATION CLASS
# ─────────────────────────────────────────────

class Station:
    def __init__(self, station_id):
        self.station_id  = station_id
        self.orders      = []
        self.busy_until  = 0
        self.is_active   = True

    def assign(self, order, current_time):
        start             = max(self.busy_until, order.arrival_time)
        order.start_time  = start
        order.finish_time = start + order.burst_time
        order.station     = self.station_id
        self.busy_until   = order.finish_time
        self.orders.append(order)

    def total_load(self):
        return sum(o.burst_time for o in self.orders)

    def __repr__(self):
        return f"Station-{self.station_id} (load={self.total_load():.1f}min)"


def make_stations(n=3):
    return [Station(i + 1) for i in range(n)]


# ─────────────────────────────────────────────
#  FCFS — First Come First Served
# ─────────────────────────────────────────────

def fcfs(orders, num_stations=3):
    """
    OS Concept: FCFS CPU Scheduling
    Orders processed in order of arrival_time.
    Each order goes to the station that is free soonest.
    """
    stations = make_stations(num_stations)
    queue    = sorted(copy.deepcopy(orders), key=lambda o: o.arrival_time)

    for order in queue:
        station = min(stations, key=lambda s: s.busy_until)
        station.assign(order, station.busy_until)

    return stations


#06c2a9bca8e12e2cba72d52067bc9801e995d1a6

# ─────────────────────────────────────────────
#  SJF — Shortest Job First
# ─────────────────────────────────────────────

def sjf(orders, num_stations=3):
    """
    OS Concept: SJF CPU Scheduling (non-preemptive)
    At each scheduling moment, pick the order with
    the smallest burst_time.
    """
    stations  = make_stations(num_stations)
    queue     = copy.deepcopy(orders)
    time      = 0

    while queue:
        available = [o for o in queue if o.arrival_time <= time]

        if not available:
            time      = min(o.arrival_time for o in queue)
            available = [o for o in queue if o.arrival_time <= time]

        order = min(available, key=lambda o: (o.burst_time, o.arrival_time))
        queue.remove(order)

        station = min(stations, key=lambda s: s.busy_until)
        station.assign(order, time)
        time = max(time, station.busy_until)

    return stations


# ─────────────────────────────────────────────
#  HYBRID SCHEDULER
# ─────────────────────────────────────────────

def hybrid_scheduler(orders, num_stations=3):
    """
    Hybrid scheduling:
    Express orders → SJF on the first N-1 stations (at least 1)
    Standard orders → FCFS on the remaining stations
    Falls back gracefully when num_stations < 3.
    """
    stations = make_stations(num_stations)

    # Guard: always keep at least 1 station for each lane
    if num_stations >= 2:
        split             = max(1, num_stations - 1)
        express_stations  = stations[:split]
        standard_stations = stations[split:]
    else:
        # Only 1 station — handle everything on it
        express_stations  = stations
        standard_stations = stations

    express  = sorted(
        [copy.deepcopy(o) for o in orders if o.delivery_type == "express"],
        key=lambda o: o.burst_time
    )
    standard = sorted(
        [copy.deepcopy(o) for o in orders if o.delivery_type == "standard"],
        key=lambda o: o.arrival_time
    )

    for order in express:
        station = min(express_stations, key=lambda s: s.busy_until)
        station.assign(order, station.busy_until)

    for order in standard:
        station = min(standard_stations, key=lambda s: s.busy_until)
        station.assign(order, station.busy_until)

    return stations


# ─────────────────────────────────────────────
#  STATION BREAKDOWN
# ─────────────────────────────────────────────

def station_breakdown(orders, fail_station=2, fail_at=30, num_stations=3):
    """
    Simulate a station failure mid-simulation.
    Station {fail_station} breaks at minute {fail_at}.
    Pending orders redistributed via SJF to active stations.

    Returns: (stations, rescued_orders)
    """
    # Clamp fail_station to valid range
    fail_station = max(1, min(fail_station, num_stations))

    stations   = make_stations(num_stations)
    queue      = copy.deepcopy(orders)
    time       = 0

    pre_queue  = [o for o in queue if o.arrival_time < fail_at]
    post_queue = [o for o in queue if o.arrival_time >= fail_at]

    # Schedule pre-breakdown orders
    for order in sorted(pre_queue, key=lambda o: o.burst_time):
        station = min(stations, key=lambda s: s.busy_until)
        station.assign(order, time)
        time = max(time, station.busy_until)

    # Trigger failure
    broken           = stations[fail_station - 1]
    broken.is_active = False

    # Orders not yet finished at fail_at are rescued
    rescued       = [o for o in broken.orders if o.finish_time > fail_at]
    broken.orders = [o for o in broken.orders if o.finish_time <= fail_at]

    # Redistribute rescued + post-breakdown orders on active stations
    active = [s for s in stations if s.is_active]

    if not active:
        # Edge case: all stations failed — reactivate all except broken
        active = [s for s in stations if s.station_id != broken.station_id]

    for order in sorted(rescued + post_queue, key=lambda o: o.burst_time):
        station = min(active, key=lambda s: s.busy_until)
        station.assign(order, station.busy_until)

    return stations, rescued