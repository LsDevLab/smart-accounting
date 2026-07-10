from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class InvoiceLine:
    line_number: int
    description: str
    amount: float
    vat_rate: float

@dataclass
class InvoiceAggregate:
    invoice_id: str
    tenant_id: str
    sender_vat: str
    receiver_vat: str
    date: datetime
    lines: List[InvoiceLine]
    total_amount: float
