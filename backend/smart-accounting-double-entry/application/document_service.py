from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from ai.agent import AccountingAIAgent
from config.settings import settings
from domain.exceptions import InvalidAccountMappingException
from models.document_model import DocumentModel
from infrastructure.repositories import DocumentRepository, AccountRepository
from schemas.document_schema import DocumentCreate, DocumentUpdate
from application.double_entry_service import DoubleEntryApplicationService

class DocumentApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)
        self.account_repo = AccountRepository(db)
        self.ai_agent = AccountingAIAgent(api_key=settings.GEMINI_API_KEY)
        self.double_entry_service = DoubleEntryApplicationService(db)

    def list_all(self, tenant_id: Optional[str] = None) -> List[DocumentModel]:
        return self.repo.list_all(tenant_id)

    def get_by_id(self, doc_id: str) -> Optional[DocumentModel]:
        return self.repo.get_by_id(doc_id)

    def create(self, schema: DocumentCreate) -> DocumentModel:
        # Create and save document
        doc = DocumentModel(
            id=schema.id,
            tenant_id=schema.tenant_id,
            description=schema.description,
            amount=schema.amount,
            vat_rate=schema.vat_rate,
            sender_vat=schema.sender_vat,
            receiver_vat=schema.receiver_vat,
            document_type=schema.document_type.value,
            created_at=datetime.utcnow(),
            status="RECEIVED"
        )
        doc = self.repo.create(doc)
        
        # Run AI mapping and Double Entry generation
        self.process_document_accounting(doc)
        return doc

    def update(self, doc_id: str, schema: DocumentUpdate) -> Optional[DocumentModel]:
        doc = self.repo.get_by_id(doc_id)
        if not doc:
            return None

        # Track if any fields affecting accounting changed
        accounting_impact = False

        if schema.description is not None:
            doc.description = schema.description
            accounting_impact = True
        if schema.amount is not None:
            doc.amount = schema.amount
            accounting_impact = True
        if schema.vat_rate is not None:
            doc.vat_rate = schema.vat_rate
            accounting_impact = True
        if schema.document_type is not None:
            doc.document_type = schema.document_type.value
            accounting_impact = True
            
        if schema.sender_vat is not None:
            doc.sender_vat = schema.sender_vat
        if schema.receiver_vat is not None:
            doc.receiver_vat = schema.receiver_vat

        # Manual overrides (if provided directly by the user)
        if schema.status is not None:
            doc.status = schema.status
        if schema.mapped_account_code is not None:
            doc.mapped_account_code = schema.mapped_account_code
            accounting_impact = True

        doc = self.repo.update(doc)

        # Re-run AI mapping and Double Entry generation if needed
        if accounting_impact:
            self.process_document_accounting(doc)

        return doc

    def delete(self, doc_id: str) -> bool:
        # Delete any associated double entry movements first
        existing_entry = self.double_entry_service.repo.get_by_document_reference(doc_id)
        if existing_entry:
            self.double_entry_service.delete(existing_entry.id)
            
        return self.repo.delete(doc_id)

    def process_document_accounting(self, doc: DocumentModel):
        """
        Interprets the document using AI, validates the account mapping,
        and generates/saves the double entry journal entries.
        """
        # Ensure default accounts are seeded so we have candidate accounts
        from application.account_service import AccountApplicationService
        account_service = AccountApplicationService(self.db)
        # Fetch accounts (this will trigger seeding if empty)
        accounts = account_service.list_all()
        
        # Prepare candidates depending on document type
        # For USCITA (expense), candidate accounts should be costs (COSTO)
        # For ENTRATA (revenue), candidate accounts should be revenues (RICAVO)
        candidates = []
        for a in accounts:
            if doc.document_type == "USCITA" and a.account_type == "COSTO":
                candidates.append({"code": a.code, "name": a.name, "account_type": a.account_type})
            elif doc.document_type == "ENTRATA" and a.account_type == "RICAVO":
                candidates.append({"code": a.code, "name": a.name, "account_type": a.account_type})

        # If no specific cost/revenue accounts, send all
        if not candidates:
            candidates = [{"code": a.code, "name": a.name, "account_type": a.account_type} for a in accounts]

        try:
            # 1. Ask Gemini to interpret the line
            ai_proposal = self.ai_agent.interpret_line(doc.description, candidates)
            proposed_name = ai_proposal.get("proposed_account")

            # 2. Validate against existing Piano dei Conti
            matched_account = None
            if proposed_name:
                # Find the account by name (case-insensitive)
                matched_account = next(
                    (a for a in accounts if a.name.strip().lower() == proposed_name.strip().lower()),
                    None
                )
                if not matched_account:
                    # Try by code if AI returned a code
                    matched_account = next(
                        (a for a in accounts if a.code == proposed_name),
                        None
                    )

            if not matched_account:
                doc.status = "FAILED"
                self.repo.update(doc)
                raise InvalidAccountMappingException(
                    f"AI proposed account '{proposed_name}' could not be validated against the Chart of Accounts."
                )

            # 3. Update document with mapping details
            doc.mapped_account_code = matched_account.code
            doc.status = "AI_ANALYZED"
            self.repo.update(doc)

            # 4. Generate double entry movements
            self.double_entry_service.generate_and_save_double_entry(doc)
            
            doc.status = "COMPLETED"
            self.repo.update(doc)

        except Exception as e:
            doc.status = "FAILED"
            self.repo.update(doc)
            # Re-raise to let controllers return appropriate HTTP responses
            raise e
