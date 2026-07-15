import sys
from collections import Counter


def drop_duplicate_barcodes(barcodes):
    counts = Counter(b.barcode for b in barcodes)
    cleaned, rejected = [], []
    for b in barcodes:
        if counts[b.barcode] == 1:
            cleaned.append(b)
        else:
            print(f"Dropping duplicate barcode: {b}", file=sys.stderr)
            rejected.append(b)
    return cleaned, rejected
