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

| Algorithm     | Type                                                  | Owner     | Purpose                          |
|---------------|-------------------------------------------------------|----------|----------------------------------|
| Merge Sort    | DAA (Divide and Conquer)                              | Mallya   | Sort orders by express + weight  |
| FCFS          | OS Scheduling (Non-preemptive, FIFO)                 | Mallika  | Arrival-order assignment         |
| SJF           | OS Scheduling (Non-preemptive, Greedy)               | Harshitha| Shortest burst time first         |
| Hybrid        | OS Scheduling (Multilevel Queue / Priority-based)    | Mallika  | SJF for express, FCFS for std    |
| Breakdown     | Fault Tolerance / Recovery + Load Rebalancing        | Harshitha| Station failure + redistribution |

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