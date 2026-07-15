import csv


def write_vouchers(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "order_id", "barcodes"])
        for customer_id, order_id, barcodes in rows:
            barcodes_str = f"[{', '.join(str(b) for b in barcodes)}]"
            writer.writerow([customer_id, order_id, barcodes_str])
