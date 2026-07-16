from models.order import Order
from models.barcode import Barcode
from csv_io.orders_reader import read_orders
from csv_io.barcodes_reader import read_barcodes
from csv_io.vouchers_writer import write_vouchers


# --- read_orders ---


def test_read_orders_valid_rows(tmp_path):
    path = tmp_path / "orders.csv"
    path.write_text("order_id,customer_id\n1,10\n2,11\n")

    result = read_orders(path)

    assert result == [Order(order_id=1, customer_id=10), Order(order_id=2, customer_id=11)]


def test_read_orders_empty_file(tmp_path):
    path = tmp_path / "orders.csv"
    path.write_text("order_id,customer_id\n")

    assert read_orders(path) == []


def test_read_orders_malformed_customer_id_skipped(tmp_path, capsys):
    path = tmp_path / "orders.csv"
    path.write_text("order_id,customer_id\n1,abc\n2,11\n")

    result = read_orders(path)

    assert result == [Order(order_id=2, customer_id=11)]
    assert "abc" in capsys.readouterr().err


def test_read_orders_malformed_order_id_skipped(tmp_path, capsys):
    path = tmp_path / "orders.csv"
    path.write_text("order_id,customer_id\nabc,10\n2,11\n")

    result = read_orders(path)

    assert result == [Order(order_id=2, customer_id=11)]
    assert "abc" in capsys.readouterr().err


def test_read_orders_missing_column_bails_early(tmp_path, capsys):
    path = tmp_path / "orders.csv"
    path.write_text("order_id,wrong_column\n1,10\n2,11\n")

    result = read_orders(path)

    assert result == []
    err = capsys.readouterr().err
    assert "missing expected column" in err
    assert err.count("missing expected column") == 1


# --- read_barcodes ---


def test_read_barcodes_valid_rows(tmp_path):
    path = tmp_path / "barcodes.csv"
    path.write_text("barcode,order_id\n11111111111,1\n11111111112,\n")

    result = read_barcodes(path)

    assert result == [
        Barcode(barcode="11111111111", order_id=1),
        Barcode(barcode="11111111112", order_id=None),
    ]


def test_read_barcodes_empty_file(tmp_path):
    path = tmp_path / "barcodes.csv"
    path.write_text("barcode,order_id\n")

    assert read_barcodes(path) == []


def test_read_barcodes_malformed_order_id_skipped(tmp_path, capsys):
    path = tmp_path / "barcodes.csv"
    path.write_text("barcode,order_id\n11111111111,abc\n11111111112,2\n")

    result = read_barcodes(path)

    assert result == [Barcode(barcode="11111111112", order_id=2)]
    assert "abc" in capsys.readouterr().err


def test_read_barcodes_missing_column_bails_early(tmp_path, capsys):
    path = tmp_path / "barcodes.csv"
    path.write_text("barcode,wrong_column\n11111111111,1\n11111111112,2\n")

    result = read_barcodes(path)

    assert result == []
    err = capsys.readouterr().err
    assert "missing expected column" in err
    assert err.count("missing expected column") == 1


# --- write_vouchers ---


def test_write_vouchers_format(tmp_path):
    path = tmp_path / "vouchers.csv"
    rows = [(10, 1, [11111111111, 11111111112])]

    write_vouchers(path, rows)

    assert path.read_text() == (
        "customer_id,order_id,barcodes\n"
        '10,1,"[11111111111, 11111111112]"\n'
    )


def test_write_vouchers_empty_rows(tmp_path):
    path = tmp_path / "vouchers.csv"

    write_vouchers(path, [])

    assert path.read_text() == "customer_id,order_id,barcodes\n"


def test_write_vouchers_accepts_generator(tmp_path):
    path = tmp_path / "vouchers.csv"
    rows = ((10, 1, [11111111111, 11111111112]) for _ in range(1))

    write_vouchers(path, rows)

    assert path.read_text() == (
        "customer_id,order_id,barcodes\n"
        '10,1,"[11111111111, 11111111112]"\n'
    )
