"""Generate a deterministic synthetic order dataset for the Nykaa support-agent capstone.

Run: python dataset.py
Prints dataset metrics, validates the acceptance criteria, and writes data/orders.json.
"""
import json
import random
from collections import Counter
from pathlib import Path

SEED = 42
NUM_ORDERS = 50
CATEGORIES = ["Apparel", "Electronics", "Home", "Footwear", "Beauty"]
STATUSES = ["Placed", "Shipped", "Delivered", "Returned", "Refunded"]
AMOUNT_MIN_INR = 299
AMOUNT_MAX_INR = 24999
DELAY_PROBABILITY = 0.20


def generate_orders(seed=SEED, num_orders=NUM_ORDERS):
    """Generate reproducible synthetic orders with required category/status coverage."""
    if num_orders < max(len(CATEGORIES) * 3, len(STATUSES)):
        raise ValueError("num_orders must allow >=3 records per category and every status.")

    rng = random.Random(seed)
    categories = CATEGORIES * 3
    statuses = STATUSES.copy()
    while len(categories) < num_orders:
        categories.append(rng.choice(CATEGORIES))
    while len(statuses) < num_orders:
        statuses.append(rng.choice(STATUSES))
    rng.shuffle(categories)
    rng.shuffle(statuses)

    orders = []
    for i in range(num_orders):
        orders.append({
            "record_id": f"NK{i + 1:04d}",
            "category": categories[i],
            "status": statuses[i],
            "order_value_inr": rng.randint(AMOUNT_MIN_INR, AMOUNT_MAX_INR),
            "days_since_created": rng.randint(0, 30),
            "delayed_shipment": rng.random() < DELAY_PROBABILITY,
        })
    return orders


def validate_orders(orders):
    """Raise ValueError if a capstone dataset requirement is not met."""
    required = {
        "record_id", "category", "status", "order_value_inr",
        "days_since_created", "delayed_shipment",
    }
    if len(orders) < 40:
        raise ValueError(f"Need at least 40 records; got {len(orders)}.")

    for i, order in enumerate(orders, 1):
        missing = required - order.keys()
        if missing:
            raise ValueError(f"Record {i} missing fields: {sorted(missing)}")
        if order["category"] not in CATEGORIES:
            raise ValueError(f"Record {i} has unknown category.")
        if order["status"] not in STATUSES:
            raise ValueError(f"Record {i} has unknown status.")
        if not isinstance(order["days_since_created"], int) or not 0 <= order["days_since_created"] <= 30:
            raise ValueError(f"Record {i}: days_since_created must be an integer from 0 to 30.")
        if not isinstance(order["delayed_shipment"], bool):
            raise ValueError(f"Record {i}: delayed_shipment must be boolean.")
        if not AMOUNT_MIN_INR <= order["order_value_inr"] <= AMOUNT_MAX_INR:
            raise ValueError(f"Record {i}: order_value_inr outside configured range.")

    category_counts = Counter(o["category"] for o in orders)
    status_counts = Counter(o["status"] for o in orders)
    delayed_count = sum(o["delayed_shipment"] for o in orders)
    delayed_percentage = delayed_count / len(orders) * 100

    for category in CATEGORIES:
        if category_counts[category] < 3:
            raise ValueError(f"Category {category} must have at least 3 records.")
    for status in STATUSES:
        if status_counts[status] < 1:
            raise ValueError(f"Status {status} must appear at least once.")
    if not 10 <= delayed_percentage <= 30:
        raise ValueError(
            f"Delayed rate {delayed_percentage:.1f}% is outside 10%-30%. "
            "Try another seed or weights; never hand-edit records."
        )

    return {
        "total_records": len(orders),
        "category_counts": dict(sorted(category_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "delayed_count": delayed_count,
        "delayed_percentage": round(delayed_percentage, 2),
    }


def main():
    orders = generate_orders()
    summary = validate_orders(orders)
    output_path = Path(__file__).resolve().parent / "data" / "orders.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(orders, indent=2), encoding="utf-8")

    print("Dataset validation: PASSED")
    print(f"Records: {summary['total_records']}")
    print(f"Seed: {SEED}")
    print(f"Order amount range: INR {AMOUNT_MIN_INR:,}–{AMOUNT_MAX_INR:,}")
    print(f"Category counts: {summary['category_counts']}")
    print(f"Status counts: {summary['status_counts']}")
    print(
        f"Delayed shipments: {summary['delayed_count']}/{summary['total_records']} "
        f"({summary['delayed_percentage']:.2f}%)"
    )
    print(f"Saved dataset to: {output_path}")


if __name__ == "__main__":
    main()
