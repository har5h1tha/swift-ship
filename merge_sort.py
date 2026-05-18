# merge_sort.py
# SwiftShip | Mallya
# Merge Sort with trace, invariant proof, and benchmark

import timeit
import copy
from order import Order
from dataset import generate_orders, SAMPLE_8

# ─────────────────────────────────────────────
#  CORE MERGE SORT
# ─────────────────────────────────────────────

def merge_sort(orders, trace=False, depth=0):
    """
    Divide & Conquer sort.
    Sorts by: express first → lighter weight first.

    CORRECTNESS INVARIANT:
    After every call to merge(left, right):
      - Every element in result is from left ∪ right
      - result is sorted by priority_key()
      - No elements are lost or duplicated
    This is maintained because we compare one element at a time
    and always append the smaller one — classic merge invariant.
    """
    if len(orders) <= 1:
        return orders

    mid   = len(orders) // 2
    left  = orders[:mid]
    right = orders[mid:]

    if trace:
        indent = "  " * depth
        print(f"{indent}DIVIDE  → LEFT:  {[o.order_id for o in left]}")
        print(f"{indent}         RIGHT: {[o.order_id for o in right]}")

    left  = merge_sort(left,  trace, depth + 1)
    right = merge_sort(right, trace, depth + 1)
    merged = merge(left, right)

    if trace:
        indent = "  " * depth
        print(f"{indent}MERGE   → {[o.order_id for o in merged]}")

    return merged


def merge(left, right):
    """
    Merge two sorted lists into one sorted list.

    LOOP INVARIANT:
    At the start of each iteration:
      result contains the (i+j) smallest elements
      in sorted order from left[0..i-1] + right[0..j-1]
    """
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        # Compare by priority: express first, then lighter weight
        if left[i].priority_key() <= right[j].priority_key():
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append remaining (already sorted)
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ─────────────────────────────────────────────
#  TRACE MODE — shows every step on 8 orders
# ─────────────────────────────────────────────

def trace_sort(orders):
    print("\n" + "="*60)
    print("  MERGE SORT — STEP BY STEP TRACE")
    print("="*60)
    print("  Input orders:")
    for o in orders:
        print(f"    {o}")
    print("\n  --- Divide & Merge steps ---")
    sorted_orders = merge_sort(copy.deepcopy(orders), trace=True)
    print("\n  --- Final sorted output ---")
    for o in sorted_orders:
        print(f"    {o}")
    print("="*60)
    return sorted_orders

