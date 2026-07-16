import csv
import sys

from models.barcode import Barcode


def read_barcodes(path):
    barcodes = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                raw_order_id = row["order_id"]
                order_id = int(raw_order_id) if raw_order_id else None
                barcode_value = row["barcode"]
            except KeyError as e:
                print(f"Barcodes CSV missing expected column: {e}", file=sys.stderr)
                break
            except ValueError:
                print(f"Skipping malformed barcode row: {row}", file=sys.stderr)
                continue

            barcodes.append(Barcode(barcode=barcode_value, order_id=order_id))
    return barcodes
