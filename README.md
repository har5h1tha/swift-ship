# SwiftShip — Order Fulfilment Engine

**Team:** Mallya · Mallika · Harshitha

A simulation of an e-commerce warehouse order fulfilment system
implementing Merge Sort (DAA) and CPU Scheduling algorithms (OS).

## How to run

```bash
git clone https://github.com/har5h1tha/SwiftShip.git
cd SwiftShip
python main.py              # basic run
python main.py --trace      # shows merge sort step-by-step trace
python main.py --chart      # saves a comparison bar chart (needs matplotlib)
```

## Algorithms implemented

| Algorithm     | Type       | Owner    | Purpose                          |
|---------------|------------|----------|----------------------------------|
| Merge Sort    | DAA D&C    | Mallya   | Sort orders by express + weight  |
| FCFS          | OS Sched   | Mallika  | Arrival-order assignment         |
| SJF           | OS Sched   | Harshitha | Shortest burst time first        |
| Hybrid        | Bonus      | Mallika | SJF for express, FCFS for std    |
| Breakdown     | Bonus      | Harshitha | Station failure + redistribution |

## File structure

```
SwiftShip/
├── main.py        ← run this
├── order.py       ← Order class
├── dataset.py     ← data generator
├── merge_sort.py  ← sorting + benchmark
├── scheduler.py   ← all 4 scheduling algorithms
├── report.py      ← comparison table + Gantt + chart
└── README.md
```