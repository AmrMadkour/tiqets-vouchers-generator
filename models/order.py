from dataclasses import dataclass

@dataclass
class Order:
    order_id: int
    customer_id: int