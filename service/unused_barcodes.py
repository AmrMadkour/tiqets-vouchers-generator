def count_unused_barcodes(barcodes):
    return sum(1 for b in barcodes if b.order_id is None)
