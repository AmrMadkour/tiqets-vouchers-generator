import sys


def drop_orders_without_barcodes(orders, barcodes):
    order_ids_with_barcodes = {b.order_id for b in barcodes if b.order_id is not None}
    cleaned, rejected = [], []
    for order in orders:
        if order.order_id in order_ids_with_barcodes:
            cleaned.append(order)
        else:
            print(f"Dropping order with zero valid barcodes: {order}", file=sys.stderr)
            rejected.append(order)
    return cleaned, rejected
