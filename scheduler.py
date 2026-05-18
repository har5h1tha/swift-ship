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

# ─────────────────────────────────────────────
#  SJF — Shortest Job First (Harshita)
# ─────────────────────────────────────────────

def sjf(orders, num_stations=3):
    """
    OS Concept: SJF CPU Scheduling (non-preemptive)
    At each scheduling moment, pick the order with
    the smallest burst_time (weight × 0.5).
    Gets express orders out faster on average.
    """
    stations  = make_stations(num_stations)
    queue     = copy.deepcopy(orders)
    scheduled = []
    time      = 0

    while queue:
        # Available orders: arrived by current time
        available = [o for o in queue if o.arrival_time <= time]

        if not available:
            # Jump time to next arrival
            time = min(o.arrival_time for o in queue)
            available = [o for o in queue if o.arrival_time <= time]

        # Pick shortest burst
        order = min(available, key=lambda o: (o.burst_time, o.arrival_time))
        queue.remove(order)

        station = min(stations, key=lambda s: s.busy_until)
        station.assign(order, time)
        time = max(time, station.busy_until)
        scheduled.append(order)

    return stations


# ─────────────────────────────────────────────
#  HYBRID SCHEDULER (Harshita)
# ─────────────────────────────────────────────

def hybrid_scheduler(orders, num_stations=3):
    """
    BONUS: Hybrid scheduling.
    Express orders → SJF on stations 1 and 2
    Standard orders → FCFS on station 3
    Runs both queues in parallel.
    """
    stations = make_stations(num_stations)
    express_stations  = stations[:2]  # stations 1 and 2
    standard_stations = stations[2:]  # station 3

    express  = sorted(
        [copy.deepcopy(o) for o in orders if o.delivery_type == "express"],
        key=lambda o: o.burst_time   # SJF
    )
    standard = sorted(
        [copy.deepcopy(o) for o in orders if o.delivery_type == "standard"],
        key=lambda o: o.arrival_time  # FCFS
    )

    for order in express:
        station = min(express_stations, key=lambda s: s.busy_until)
        station.assign(order, station.busy_until)

    for order in standard:
        station = min(standard_stations, key=lambda s: s.busy_until)

        station.assign(order, station.busy_until)

    return stations



# ─────────────────────────────────────────────
#  STATION BREAKDOWN (Harshita)
# ─────────────────────────────────────────────

def station_breakdown(orders, fail_station=2, fail_at=30, num_stations=3):
    """
    BONUS: Simulate a station failure mid-simulation.
    Station {fail_station} breaks at minute {fail_at}.
    Its pending orders are redistributed using SJF
    to the remaining active stations.
    """
    stations = make_stations(num_stations)
    queue    = copy.deepcopy(orders)
    time     = 0

    print(f"\n  [BREAKDOWN SIMULATION]")
    print(f"  Station {fail_station} will FAIL at t={fail_at} min\n")

    # Process orders until the breakdown moment
    pre_queue  = [o for o in queue if o.arrival_time < fail_at]
    post_queue = [o for o in queue if o.arrival_time >= fail_at]

    for order in sorted(pre_queue, key=lambda o: o.burst_time):
        station = min(stations, key=lambda s: s.busy_until)
        station.assign(order, time)
        time = max(time, station.busy_until)

    # Simulate failure
    broken = stations[fail_station - 1]
    broken.is_active = False
    rescued = [o for o in broken.orders if o.finish_time > fail_at]
    broken.orders = [o for o in broken.orders if o.finish_time <= fail_at]

    print(f"  !! Station {fail_station} broke down at t={fail_at}min !!")
    print(f"  Rescued {len(rescued)} orders → redistributing via SJF...\n")

    active = [s for s in stations if s.is_active]
    for order in sorted(rescued + post_queue, key=lambda o: o.burst_time):
        station = min(active, key=lambda s: s.busy_until)
        station.assign(order, station.busy_until)

    return stations
