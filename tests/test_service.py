from models.order import Order
from models.barcode import Barcode
from service.grouping import group_barcodes, build_rows
from service.top_customers import top_5_customers
from service.unused_barcodes import count_unused_barcodes


# --- group_barcodes ---


def test_group_barcodes_basic():
    orders = [Order(order_id=1, customer_id=10), Order(order_id=2, customer_id=10)]
    barcodes = [Barcode(barcode="A", order_id=1), Barcode(barcode="B", order_id=1), Barcode(barcode="C", order_id=2)]

    result = group_barcodes(orders, barcodes)

    assert result == {(10, 1): ["A", "B"], (10, 2): ["C"]}


def test_group_barcodes_ignores_unsold_barcodes():
    orders = [Order(order_id=1, customer_id=10)]
    barcodes = [Barcode(barcode="A", order_id=1), Barcode(barcode="B", order_id=None)]

    result = group_barcodes(orders, barcodes)

    assert result == {(10, 1): ["A"]}


def test_group_barcodes_empty_input():
    assert group_barcodes([], []) == {}


def test_group_barcodes_skips_unknown_order_id(capsys):
    orders = [Order(order_id=1, customer_id=10)]
    barcodes = [Barcode(barcode="A", order_id=1), Barcode(barcode="B", order_id=999)]

    result = group_barcodes(orders, barcodes)

    assert result == {(10, 1): ["A"]}
    assert "999" in capsys.readouterr().err


# --- build_rows ---


def test_build_rows_yields_tuples():
    grouped = {(10, 1): ["A", "B"]}

    result = list(build_rows(grouped))

    assert result == [(10, 1, ["A", "B"])]


def test_build_rows_empty_input():
    assert list(build_rows({})) == []


# --- top_5_customers ---


def test_top_5_customers_sorted_by_ticket_count_desc():
    grouped = {(10, 1): ["A"], (20, 2): ["B", "C", "D"], (30, 3): ["E", "F"]}

    result = top_5_customers(grouped)

    assert result == [(20, 3), (30, 2), (10, 1)]


def test_top_5_customers_limits_to_five():
    grouped = {(i, i): ["A"] * i for i in range(1, 8)}  # 7 customers, ticket counts 1..7

    result = top_5_customers(grouped)

    assert len(result) == 5
    assert result == [(7, 7), (6, 6), (5, 5), (4, 4), (3, 3)]


def test_top_5_customers_ties_broken_by_customer_id_asc():
    grouped = {(30, 1): ["A"], (10, 2): ["B"], (20, 3): ["C"]}

    result = top_5_customers(grouped)

    assert result == [(10, 1), (20, 1), (30, 1)]


def test_top_5_customers_sums_multiple_orders_per_customer():
    grouped = {(10, 1): ["A"], (10, 2): ["B"]}

    result = top_5_customers(grouped)

    assert result == [(10, 2)]


def test_top_5_customers_empty_input():
    assert top_5_customers({}) == []


# --- count_unused_barcodes ---


def test_count_unused_barcodes_mixed():
    barcodes = [Barcode(barcode="A", order_id=1), Barcode(barcode="B", order_id=None), Barcode(barcode="C", order_id=None)]

    assert count_unused_barcodes(barcodes) == 2


def test_count_unused_barcodes_empty_input():
    assert count_unused_barcodes([]) == 0
