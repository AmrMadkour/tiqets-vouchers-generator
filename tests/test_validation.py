from models.order import Order
from models.barcode import Barcode
from validation.duplicate_barcodes import drop_duplicate_barcodes
from validation.orphaned_orders import drop_orders_without_barcodes


# --- drop_duplicate_barcodes ---


def test_drop_duplicate_barcodes_no_duplicates():
    barcodes = [Barcode(barcode="A", order_id=1), Barcode(barcode="B", order_id=1)]

    cleaned, rejected = drop_duplicate_barcodes(barcodes)

    assert cleaned == barcodes
    assert rejected == []


def test_drop_duplicate_barcodes_drops_all_occurrences(capsys):
    barcodes = [
        Barcode(barcode="A", order_id=1),
        Barcode(barcode="A", order_id=2),
        Barcode(barcode="B", order_id=1),
    ]

    cleaned, rejected = drop_duplicate_barcodes(barcodes)

    assert cleaned == [Barcode(barcode="B", order_id=1)]
    assert rejected == [Barcode(barcode="A", order_id=1), Barcode(barcode="A", order_id=2)]
    assert "A" in capsys.readouterr().err


def test_drop_duplicate_barcodes_empty_input():
    assert drop_duplicate_barcodes([]) == ([], [])


def test_drop_duplicate_barcodes_all_duplicates():
    barcodes = [Barcode(barcode="A", order_id=1), Barcode(barcode="A", order_id=2)]

    cleaned, rejected = drop_duplicate_barcodes(barcodes)

    assert cleaned == []
    assert rejected == barcodes


# --- drop_orders_without_barcodes ---


def test_drop_orders_without_barcodes_keeps_orders_with_barcodes():
    orders = [Order(order_id=1, customer_id=10)]
    barcodes = [Barcode(barcode="A", order_id=1)]

    cleaned, rejected = drop_orders_without_barcodes(orders, barcodes)

    assert cleaned == orders
    assert rejected == []


def test_drop_orders_without_barcodes_drops_orphaned_orders(capsys):
    orders = [Order(order_id=1, customer_id=10), Order(order_id=2, customer_id=11)]
    barcodes = [Barcode(barcode="A", order_id=1)]

    cleaned, rejected = drop_orders_without_barcodes(orders, barcodes)

    assert cleaned == [Order(order_id=1, customer_id=10)]
    assert rejected == [Order(order_id=2, customer_id=11)]
    assert "2" in capsys.readouterr().err


def test_drop_orders_without_barcodes_ignores_unsold_barcodes():
    orders = [Order(order_id=1, customer_id=10)]
    barcodes = [Barcode(barcode="A", order_id=None)]

    cleaned, rejected = drop_orders_without_barcodes(orders, barcodes)

    assert cleaned == []
    assert rejected == orders


def test_drop_orders_without_barcodes_empty_input():
    assert drop_orders_without_barcodes([], []) == ([], [])


def test_drop_orders_without_barcodes_all_valid():
    orders = [Order(order_id=1, customer_id=10), Order(order_id=2, customer_id=11)]
    barcodes = [Barcode(barcode="A", order_id=1), Barcode(barcode="B", order_id=2)]

    cleaned, rejected = drop_orders_without_barcodes(orders, barcodes)

    assert cleaned == orders
    assert rejected == []
