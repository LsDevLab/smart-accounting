from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class EntryMovement:
    account_code: str
    account_name: str
    is_debit: bool
    amount: float

@dataclass
class JournalEntryAggregate:
    entry_id: str
    tenant_id: str
    document_reference: str
    date: datetime
    movements: List[EntryMovement]

    def is_balanced(self) -> bool:
        debits = sum(m.amount for m in self.movements if m.is_debit)
        credits = sum(m.amount for m in self.movements if not m.is_debit)
        return abs(debits - credits) < 1e-6
