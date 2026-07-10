import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from domain.rules import AccountingValidationRules
from domain.exceptions import UnbalancedEntryException, InvalidAccountMappingException
from models.journal_entry_model import JournalEntryModel
from models.double_entry_line_model import DoubleEntryLineModel
from infrastructure.repositories import JournalEntryRepository, AccountRepository
from schemas.double_entry_schema import JournalEntryCreate, JournalEntryUpdate, DoubleEntryLineCreate

# Standard Account Constants
DEBITI_FORNITORI_CODE = "450001"
CREDITI_CLIENTI_CODE = "110001"
IVA_CREDITO_CODE = "220001"
IVA_DEBITO_CODE = "220002"

class DoubleEntryApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = JournalEntryRepository(db)
        self.account_repo = AccountRepository(db)

    def _ensure_standard_accounts(self):
        """Ensures standard system accounts exist in the Piano dei Conti."""
        from models.account_model import AccountModel
        standards = [
            (DEBITI_FORNITORI_CODE, "Debiti verso Fornitori", "PASSIVO"),
            (CREDITI_CLIENTI_CODE, "Crediti verso Clienti", "ATTIVO"),
            (IVA_CREDITO_CODE, "IVA a Credito", "ATTIVO"),
            (IVA_DEBITO_CODE, "IVA a Debito", "PASSIVO"),
        ]
        for code, name, type_ in standards:
            if not self.account_repo.get_by_code(code):
                acc = AccountModel(code=code, name=name, account_type=type_)
                self.account_repo.create(acc)

    def list_all(self, tenant_id: Optional[str] = None) -> List[JournalEntryModel]:
        return self.repo.list_all(tenant_id)

    def get_by_id(self, entry_id: str) -> Optional[JournalEntryModel]:
        return self.repo.get_by_id(entry_id)

    def delete(self, entry_id: str) -> bool:
        return self.repo.delete(entry_id)

    def create_manual_entry(self, schema: JournalEntryCreate) -> JournalEntryModel:
        # Validate that the movements are balanced
        debits_sum = sum(m.amount for m in schema.movements if m.is_debit)
        credits_sum = sum(m.amount for m in schema.movements if not m.is_debit)

        if not AccountingValidationRules.validate_double_entry(debits_sum, credits_sum):
            raise UnbalancedEntryException(
                f"Double entry is not balanced. Debits: {debits_sum}, Credits: {credits_sum}"
            )

        # Validate accounts exist
        for m in schema.movements:
            if not self.account_repo.get_by_code(m.account_code):
                raise InvalidAccountMappingException(f"Account with code '{m.account_code}' does not exist.")

        # Delete any existing entry with the same reference
        if schema.document_reference:
            existing = self.repo.get_by_document_reference(schema.document_reference)
            if existing:
                self.repo.delete(existing.id)

        # Create entry header
        entry = JournalEntryModel(
            id=schema.id,
            tenant_id=schema.tenant_id,
            entry_date=schema.entry_date,
            document_reference=schema.document_reference
        )

        # Create entry lines
        lines = []
        for m in schema.movements:
            line = DoubleEntryLineModel(
                id=str(uuid.uuid4()),
                journal_entry_id=entry.id,
                account_code=m.account_code,
                is_debit=m.is_debit,
                amount=m.amount
            )
            lines.append(line)

        entry.lines = lines
        return self.repo.create(entry)

    def update_manual_entry(self, entry_id: str, schema: JournalEntryUpdate) -> Optional[JournalEntryModel]:
        entry = self.repo.get_by_id(entry_id)
        if not entry:
            return None

        if schema.entry_date is not None:
            entry.entry_date = schema.entry_date
        if schema.document_reference is not None:
            entry.document_reference = schema.document_reference

        if schema.movements is not None:
            # Validate that the updated movements are balanced
            debits_sum = sum(m.amount for m in schema.movements if m.is_debit)
            credits_sum = sum(m.amount for m in schema.movements if not m.is_debit)

            if not AccountingValidationRules.validate_double_entry(debits_sum, credits_sum):
                raise UnbalancedEntryException(
                    f"Double entry is not balanced. Debits: {debits_sum}, Credits: {credits_sum}"
                )

            # Validate accounts exist
            for m in schema.movements:
                if not self.account_repo.get_by_code(m.account_code):
                    raise InvalidAccountMappingException(f"Account with code '{m.account_code}' does not exist.")

            # Clear old lines and add new ones
            entry.lines.clear()
            for m in schema.movements:
                line = DoubleEntryLineModel(
                    id=str(uuid.uuid4()),
                    journal_entry_id=entry.id,
                    account_code=m.account_code,
                    is_debit=m.is_debit,
                    amount=m.amount
                )
                entry.lines.append(line)

        self.db.commit()
        self.db.refresh(entry)
        return entry

    def generate_and_save_double_entry(self, document) -> JournalEntryModel:
        """
        Generates and persists double entry movements for a Document.
        """
        self._ensure_standard_accounts()
        
        # 1. Calculate taxable amount and VAT amount
        taxable_amount = round(document.amount / (1.0 + document.vat_rate), 2)
        vat_amount = round(document.amount - taxable_amount, 2)
        
        # Adjust potential rounding diff to keep the total exact
        # For example, if taxable_amount + vat_amount != document.amount, adjust taxable_amount
        if taxable_amount + vat_amount != document.amount:
            taxable_amount = round(document.amount - vat_amount, 2)

        movements = []

        if document.document_type == "USCITA":
            # Purchase Expense (passive invoice):
            # Debit: Expense (mapped account)
            # Debit: VAT a Credito
            # Credit: Debiti verso Fornitori (total)
            movements.append(DoubleEntryLineCreate(
                account_code=document.mapped_account_code,
                is_debit=True,
                amount=taxable_amount
            ))
            if vat_amount > 0:
                movements.append(DoubleEntryLineCreate(
                    account_code=IVA_CREDITO_CODE,
                    is_debit=True,
                    amount=vat_amount
                ))
            movements.append(DoubleEntryLineCreate(
                account_code=DEBITI_FORNITORI_CODE,
                is_debit=False,
                amount=document.amount
            ))
        else:
            # Sales Revenue (active invoice):
            # Debit: Crediti verso Clienti (total)
            # Credit: Revenue (mapped account)
            # Credit: VAT a Debito
            movements.append(DoubleEntryLineCreate(
                account_code=CREDITI_CLIENTI_CODE,
                is_debit=True,
                amount=document.amount
            ))
            movements.append(DoubleEntryLineCreate(
                account_code=document.mapped_account_code,
                is_debit=False,
                amount=taxable_amount
            ))
            if vat_amount > 0:
                movements.append(DoubleEntryLineCreate(
                    account_code=IVA_DEBITO_CODE,
                    is_debit=False,
                    amount=vat_amount
                ))

        # Build and invoke creation through the standard pipeline
        je_create = JournalEntryCreate(
            id=f"JE-{document.id}",
            tenant_id=document.tenant_id,
            entry_date=document.created_at,
            document_reference=document.id,
            movements=movements
        )
        return self.create_manual_entry(je_create)
