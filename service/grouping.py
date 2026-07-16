import sys
from collections import defaultdict


def group_barcodes(orders, barcodes):
    order_customer = {o.order_id: o.customer_id for o in orders}

    barcodes_by_order = defaultdict(list)
    for b in barcodes:
        if b.order_id is not None:
            barcodes_by_order[b.order_id].append(b.barcode)

    grouped = {}
    for order_id, barcode_list in barcodes_by_order.items():
        customer_id = order_customer.get(order_id)
        if customer_id is None:
            print(f"Skipping barcodes for unknown order_id: {order_id}", file=sys.stderr)
            continue
        grouped[(customer_id, order_id)] = barcode_list

    return grouped


def build_rows(grouped):
    for (customer_id, order_id), barcodes in grouped.items():
        yield (customer_id, order_id, barcodes)
