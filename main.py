
# Usage: python main.py
#        python main.py --trace    (shows merge sort trace)
#        python main.py --chart    (saves matplotlib chart)

import sys
from dataset     import generate_orders, SAMPLE_8, print_orders
from merge_sort  import trace_sort, merge_sort, benchmark
from scheduler   import fcfs, sjf, hybrid_scheduler, station_breakdown
from report      import print_report, print_gantt, save_chart

def main():
    do_trace = "--trace" in sys.argv
    do_chart = "--chart" in sys.argv

    print("\n" + "#"*60)
    print("#       SWIFTSHIP ORDER FULFILMENT ENGINE              #")
    print("#       Team: Mallya | Mallika | Harshita              #")
    print("#"*60)

    # ── STEP 1: Generate Data ──────────────────────────────────
    print("\n[STEP 1] Generating 100 orders...")
    orders = generate_orders(100, seed=42)
    print(f"  {len(orders)} orders created.")
    print(f"  Express: {sum(1 for o in orders if o.delivery_type=='express')}")
    print(f"  Standard: {sum(1 for o in orders if o.delivery_type=='standard')}")

    # ── STEP 2: Merge Sort ─────────────────────────────────────
    print("\n[STEP 2] Sorting orders with Merge Sort...")
    if do_trace:
        print("\n  --- Trace on 8 sample orders ---")
        trace_sort(SAMPLE_8)

    sorted_orders = merge_sort(orders)
    print(f"  First 5 after sort:")
    for o in sorted_orders[:5]:
        print(f"    {o}")

    print("\n[STEP 2b] Benchmark (1000 orders):")
    benchmark(1000)

    # ── STEP 3: Scheduling ─────────────────────────────────────
    print("\n[STEP 3] Running scheduling algorithms on 3 stations...")

    print("\n  Running FCFS...")
    fcfs_stations    = fcfs(sorted_orders, num_stations=3)

    print("  Running SJF...")
    sjf_stations     = sjf(sorted_orders, num_stations=3)

    print("  Running Hybrid (express=SJF, standard=FCFS)...")
    hybrid_stations  = hybrid_scheduler(sorted_orders, num_stations=3)

    # ── STEP 4: Report ─────────────────────────────────────────
    print("\n[STEP 4] Generating comparison report...")
    results = {
        "FCFS"  : fcfs_stations,
        "SJF"   : sjf_stations,
        "Hybrid": hybrid_stations,
    }
    print_report(results)

    # ── STEP 5: Gantt Charts ───────────────────────────────────
    print("\n[STEP 5] Gantt charts (first 5 orders per station):")
    for name, stations in results.items():
        # Limit to first 5 per station for readability
        for s in stations:
            s.orders = s.orders[:5]
        print_gantt(stations, title=f"{name} — Station Load")

    # ── STEP 6: Bonus — Station Breakdown ─────────────────────
    print("\n[STEP 6] BONUS — Station Breakdown Simulation:")
    breakdown_stations = station_breakdown(sorted_orders, fail_station=2, fail_at=30)
    print_gantt(breakdown_stations, title="After Station 2 Breakdown")

    # ── STEP 7: Chart (optional) ───────────────────────────────
    if do_chart:
        print("\n[STEP 7] Saving comparison chart...")
        # Regenerate full stations for accurate chart data
        results_full = {
            "FCFS"  : fcfs(sorted_orders),
            "SJF"   : sjf(sorted_orders),
            "Hybrid": hybrid_scheduler(sorted_orders),
        }
        save_chart(results_full)

    print("\n" + "#"*60)
    print("#  Simulation complete. SwiftShip is ready to ship!    #")
    print("#"*60 + "\n")

if __name__ == "__main__":
    main()