import pytest

from main import main


def test_main_missing_orders_file(tmp_path, capsys):
    barcodes_path = tmp_path / "barcodes.csv"
    barcodes_path.write_text("barcode,order_id\n11111111111,1\n")

    with pytest.raises(SystemExit):
        main(str(tmp_path / "missing_orders.csv"), str(barcodes_path))

    assert "missing_orders.csv" in capsys.readouterr().err


def test_main_missing_barcodes_file(tmp_path, capsys):
    orders_path = tmp_path / "orders.csv"
    orders_path.write_text("order_id,customer_id\n1,10\n")

    with pytest.raises(SystemExit):
        main(str(orders_path), str(tmp_path / "missing_barcodes.csv"))

    assert "missing_barcodes.csv" in capsys.readouterr().err
