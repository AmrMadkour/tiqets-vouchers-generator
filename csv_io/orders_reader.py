import csv
import sys

from models.order import Order


def read_orders(path):
    orders = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                order_id = int(row["order_id"])
                customer_id = int(row["customer_id"])
            except KeyError as e:
                print(f"Orders CSV missing expected column: {e}", file=sys.stderr)
                break
            except ValueError:
                print(f"Skipping malformed order row: {row}", file=sys.stderr)
                continue

            orders.append(Order(order_id=order_id, customer_id=customer_id))
    return orders
