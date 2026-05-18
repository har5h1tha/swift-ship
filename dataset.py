# dataset.py
# SwiftShip 
# Generates random order datasets for simulation

import random
from order import Order

SAMPLE_8 = [
    Order("ORD001", 3.2,  "express",  5),
    Order("ORD002", 12.0, "standard", 2),
    Order("ORD003", 1.5,  "express",  8),
    Order("ORD004", 7.8,  "standard", 1),
    Order("ORD005", 0.8,  "express",  10),
    Order("ORD006", 5.5,  "standard", 3),
    Order("ORD007", 2.1,  "express",  6),
    Order("ORD008", 9.0,  "standard", 4),
]

def generate_orders(n=100, seed=42):
    """
    Generate n random orders.
    seed=42 ensures reproducible results every run.
    """
    random.seed(seed)
    orders = []
    for i in range(1, n + 1):
        weight       = round(random.uniform(0.5, 20.0), 1)
        delivery     = random.choices(
                           ["express", "standard"],
                           weights=[30, 70]  # 30% express, 70% standard
                       )[0]
        arrival_time = random.randint(0, 60)
        orders.append(Order(f"ORD{i:03}", weight, delivery, arrival_time))
    return orders

def print_orders(orders, title="Orders"):
    print(f"\n{'='*60}")
    print(f"  {title}  ({len(orders)} orders)")
    print(f"{'='*60}")
    for o in orders:
        print(f"  {o}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    orders = generate_orders(10)
    print_orders(orders, "Sample 10 Orders")