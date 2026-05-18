# report.py
# SwiftShip | Harshita
# Prints formatted comparison report and optional chart

def compute_metrics(stations):
    """
    Extracts all orders from stations and computes:
    - Average waiting time
    - Average turnaround time
    - Total orders shipped
    - First express order finish time
    - Throughput (orders per hour)
    - Makespan
    - Station loads (dict of station_id -> total burst time)
    """
    all_orders = []
    for station in stations:
        all_orders.extend(station.orders)

    if not all_orders:
        return {
            "total_orders"     : 0,
            "express_count"    : 0,
            "avg_waiting"      : 0,
            "avg_turnaround"   : 0,
            "first_express_out": None,
            "makespan"         : 0,
            "throughput"       : 0,
            "station_loads"    : {},
        }

    waiting    = [o.waiting_time()    for o in all_orders if o.waiting_time()    is not None]
    turnaround = [o.turnaround_time() for o in all_orders if o.turnaround_time() is not None]

    express_done  = [o for o in all_orders if o.delivery_type == "express" and o.finish_time]
    first_express = min(o.finish_time for o in express_done) if express_done else None

    finish_times  = [o.finish_time for o in all_orders if o.finish_time is not None]
    makespan      = max(finish_times) if finish_times else 0

    # Throughput: orders completed per hour (60 min)
    throughput = round((len(all_orders) / makespan) * 60, 2) if makespan > 0 else 0

    # Station loads: station_id -> total burst time assigned
    station_loads = {}
    for station in stations:
        station_loads[station.station_id] = round(
            sum(o.burst_time for o in station.orders), 2
        )

    return {
        "total_orders"     : len(all_orders),
        "express_count"    : len(express_done),
        "avg_waiting"      : round(sum(waiting) / len(waiting), 2) if waiting else 0,
        "avg_turnaround"   : round(sum(turnaround) / len(turnaround), 2) if turnaround else 0,
        "first_express_out": first_express,
        "makespan"         : makespan,
        "throughput"       : throughput,
        "station_loads"    : station_loads,
    }


def print_report(results: dict):
    """
    results = {"FCFS": stations, "SJF": stations, "Hybrid": stations}
    """
    metrics = {name: compute_metrics(stations) for name, stations in results.items()}

    print("\n" + "="*70)
    print("  SWIFTSHIP — SCHEDULING ALGORITHM COMPARISON REPORT")
    print("="*70)

    headers = ["Metric", *metrics.keys()]
    rows = [
        ["Total orders",       *[str(m["total_orders"])      for m in metrics.values()]],
        ["Express orders",     *[str(m["express_count"])     for m in metrics.values()]],
        ["Avg waiting time",   *[f"{m['avg_waiting']}min"    for m in metrics.values()]],
        ["Avg turnaround",     *[f"{m['avg_turnaround']}min" for m in metrics.values()]],
        ["First express out",  *[f"t={m['first_express_out']}min" if m['first_express_out'] else "N/A" for m in metrics.values()]],
        ["Total makespan",     *[f"{m['makespan']}min"       for m in metrics.values()]],
        ["Throughput",         *[f"{m['throughput']} ord/hr" for m in metrics.values()]],
    ]

    col_w = 22
    header_line = "  " + " | ".join(h.ljust(col_w) for h in headers)
    print(header_line)
    print("  " + "-" * (len(header_line) - 2))
    for row in rows:
        print("  " + " | ".join(cell.ljust(col_w) for cell in row))

    print("="*70)

    best_wait = min(metrics, key=lambda k: metrics[k]["avg_waiting"])
    best_turn = min(metrics, key=lambda k: metrics[k]["avg_turnaround"])
    best_exp  = min(metrics, key=lambda k: metrics[k]["first_express_out"] or 9999)

    print(f"\n  Best avg waiting time : {best_wait}")
    print(f"  Best avg turnaround   : {best_turn}")
    print(f"  Fastest express out   : {best_exp}")
    print("="*70 + "\n")


def print_gantt(stations, title="Gantt Chart"):
    print(f"\n  {title}")
    print("  " + "-"*60)
    for station in stations:
        status = "ACTIVE" if station.is_active else "FAILED"
        print(f"  Station {station.station_id} [{status}]:")
        for o in station.orders:
            bar = "#" * int(o.burst_time)
            print(f"    t={o.start_time:>4.0f}-{o.finish_time:<4.0f}  "
                  f"{bar:<20}  {o.order_id} ({o.delivery_type})")
    print("  " + "-"*60 + "\n")


def save_chart(results: dict, filename="swiftship_chart.png"):
    try:
        import matplotlib.pyplot as plt
        metrics = {name: compute_metrics(s) for name, s in results.items()}

        labels   = list(metrics.keys())
        wait     = [metrics[k]["avg_waiting"]    for k in labels]
        turn     = [metrics[k]["avg_turnaround"] for k in labels]
        express  = [metrics[k]["first_express_out"] or 0 for k in labels]

        x  = range(len(labels))
        w  = 0.25

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar([i - w for i in x],  wait,    w, label="Avg Wait (min)",       color="#7F77DD")
        ax.bar([i     for i in x],  turn,    w, label="Avg Turnaround (min)", color="#1D9E75")
        ax.bar([i + w for i in x],  express, w, label="First Express Out",    color="#D85A30")

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_ylabel("Minutes")
        ax.set_title("SwiftShip — Scheduling Algorithm Comparison")
        ax.legend()
        plt.tight_layout()
        plt.savefig(filename)
        print(f"  Chart saved to {filename}")
        plt.show()
    except ImportError:
        print("  matplotlib not installed — skipping chart. Run: pip install matplotlib")