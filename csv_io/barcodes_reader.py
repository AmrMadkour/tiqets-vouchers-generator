import csv
import sys

from models.barcode import Barcode


def read_barcodes(path):
    barcodes = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_order_id = row["order_id"]
            try:
                order_id = int(raw_order_id) if raw_order_id else None
            except ValueError:
                print(f"Skipping malformed barcode row: {row}", file=sys.stderr)
                continue
            barcodes.append(Barcode(barcode=row["barcode"], order_id=order_id))
    return barcodes
