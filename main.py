import sys

from csv_io.orders_reader import read_orders
from csv_io.barcodes_reader import read_barcodes
from csv_io.vouchers_writer import write_vouchers
from validation.duplicate_barcodes import drop_duplicate_barcodes
from validation.orphaned_orders import drop_orders_without_barcodes
from service.grouping import group_barcodes, build_rows
from service.top_customers import top_5_customers
from service.unused_barcodes import count_unused_barcodes


def main(orders_path, barcodes_path, output_path="vouchers.csv"):
    raw_orders = read_orders(orders_path)
    raw_barcodes = read_barcodes(barcodes_path)

    cleaned_barcodes, _ = drop_duplicate_barcodes(raw_barcodes)
    cleaned_orders, _ = drop_orders_without_barcodes(raw_orders, cleaned_barcodes)

    grouped = group_barcodes(cleaned_orders, cleaned_barcodes)
    write_vouchers(output_path, build_rows(grouped))

    for customer_id, ticket_count in top_5_customers(grouped):
        print(f"{customer_id},{ticket_count}")

    print(f"Unused barcodes: {count_unused_barcodes(cleaned_barcodes)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <orders.csv> <barcodes.csv> [output.csv]", file=sys.stderr)
        sys.exit(1)

    output = sys.argv[3] if len(sys.argv) > 3 else "vouchers.csv"
    main(sys.argv[1], sys.argv[2], output)
