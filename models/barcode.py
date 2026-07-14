from dataclasses import dataclass

@dataclass
class Barcode:
    barcode: str
    order_id: int | None