import pytest
from datetime import datetime
from application.account_service import AccountApplicationService
from application.document_service import DocumentApplicationService
from application.double_entry_service import DoubleEntryApplicationService
from schemas.account_schema import AccountCreate, AccountType, AccountUpdate
from schemas.document_schema import DocumentCreate, DocumentType, DocumentUpdate
from domain.exceptions import InvalidAccountMappingException, UnbalancedEntryException

def test_account_service_crud_and_seeding(db):
    account_service = AccountApplicationService(db)
    
    # 1. Seeding check (listing seeds if empty)
    accounts = account_service.list_all()
    assert len(accounts) > 0
    assert any(a.code == "600001" for a in accounts)

    # 2. Create account
    new_acc = AccountCreate(code="999999", name="Test Account", account_type=AccountType.COSTO)
    created = account_service.create(new_acc)
    assert created.code == "999999"
    assert created.name == "Test Account"

    # 3. Read account
    retrieved = account_service.get_by_code("999999")
    assert retrieved is not None
    assert retrieved.name == "Test Account"

    # 4. Update account
    updated = account_service.update("999999", AccountUpdate(name="Updated Test Account", account_type=AccountType.COSTO))
    assert updated.name == "Updated Test Account"

    # 5. Delete account
    assert account_service.delete("999999") is True
    assert account_service.get_by_code("999999") is None

def test_document_creation_and_automatic_double_entry(db):
    # Ensure accounts are seeded first
    account_service = AccountApplicationService(db)
    account_service.seed_default_accounts()

    doc_service = DocumentApplicationService(db)
    de_service = DoubleEntryApplicationService(db)

    # 1. Create a purchase document (USCITA)
    # The description "Manutenzione climatizzatori" contains "Manutenzione", so mock AI will map to "Spese di Manutenzione Immobili" (600001)
    doc_create = DocumentCreate(
        id="DOC-001",
        tenant_id="TENANT-A",
        description="Fattura per Manutenzione climatizzatori",
        amount=1220.00,
        vat_rate=0.22,
        sender_vat="IT12345678901",
        receiver_vat="IT98765432109",
        document_type=DocumentType.USCITA
    )

    doc = doc_service.create(doc_create)

    # Assert document state
    assert doc.id == "DOC-001"
    assert doc.status == "COMPLETED"
    assert doc.mapped_account_code == "600001" # Spese di Manutenzione Immobili

    # Assert double entry movements generated
    je = de_service.repo.get_by_document_reference("DOC-001")
    assert je is not None
    assert je.tenant_id == "TENANT-A"
    
    # Movements should be:
    # Debit 600001: 1000.00 (Taxable)
    # Debit 220001: 220.00 (VAT a Credito)
    # Credit 450001: 1220.00 (Debiti verso Fornitori)
    assert len(je.lines) == 3
    
    debits = [l for l in je.lines if l.is_debit]
    credits = [l for l in je.lines if not l.is_debit]
    
    assert len(debits) == 2
    assert len(credits) == 1
    
    expense_line = next(l for l in debits if l.account_code == "600001")
    vat_line = next(l for l in debits if l.account_code == "220001")
    supplier_line = credits[0]
    
    assert expense_line.amount == 1000.00
    assert vat_line.amount == 220.00
    assert supplier_line.account_code == "450001"
    assert supplier_line.amount == 1220.00

def test_document_update_recalculates_double_entry(db):
    account_service = AccountApplicationService(db)
    account_service.seed_default_accounts()

    doc_service = DocumentApplicationService(db)
    de_service = DoubleEntryApplicationService(db)

    # Create initial document
    doc = doc_service.create(DocumentCreate(
        id="DOC-002",
        tenant_id="TENANT-A",
        description="Fattura per Manutenzione",
        amount=1220.00,
        vat_rate=0.22,
        document_type=DocumentType.USCITA
    ))

    # Initial double entry check
    je_initial = de_service.repo.get_by_document_reference("DOC-002")
    assert len(je_initial.lines) == 3

    # Update document amount and description to "Energia Elettrica" (should map to 600003)
    doc_service.update("DOC-002", DocumentUpdate(
        description="Bolletta Energia Elettrica",
        amount=244.00,
        vat_rate=0.22
    ))

    # Refetched document details
    doc_updated = doc_service.get_by_id("DOC-002")
    assert doc_updated.mapped_account_code == "600003" # Costo Energia Elettrica
    assert doc_updated.amount == 244.00

    # New double entry check (should be updated)
    je_updated = de_service.repo.get_by_document_reference("DOC-002")
    assert len(je_updated.lines) == 3
    
    debits = [l for l in je_updated.lines if l.is_debit]
    expense_line = next(l for l in debits if l.account_code == "600003")
    vat_line = next(l for l in debits if l.account_code == "220001")
    supplier_line = next(l for l in je_updated.lines if not l.is_debit)

    assert expense_line.amount == 200.00
    assert vat_line.amount == 44.00
    assert supplier_line.amount == 244.00

def test_document_deletion_removes_double_entry(db):
    account_service = AccountApplicationService(db)
    account_service.seed_default_accounts()

    doc_service = DocumentApplicationService(db)
    de_service = DoubleEntryApplicationService(db)

    doc = doc_service.create(DocumentCreate(
        id="DOC-003",
        tenant_id="TENANT-A",
        description="Fattura per Manutenzione",
        amount=1220.00,
        vat_rate=0.22,
        document_type=DocumentType.USCITA
    ))

    # Assert journal entry exists
    assert de_service.repo.get_by_document_reference("DOC-003") is not None

    # Delete document
    assert doc_service.delete("DOC-003") is True
    
    # Assert document and journal entry are both gone
    assert doc_service.get_by_id("DOC-003") is None
    assert de_service.repo.get_by_document_reference("DOC-003") is None
