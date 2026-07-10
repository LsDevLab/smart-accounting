from sqlalchemy.orm import Session
from typing import List, Optional
from models.account_model import AccountModel
from models.document_model import DocumentModel
from models.journal_entry_model import JournalEntryModel
from models.double_entry_line_model import DoubleEntryLineModel

class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str) -> Optional[AccountModel]:
        return self.db.query(AccountModel).filter(AccountModel.code == code).first()

    def get_by_name(self, name: str) -> Optional[AccountModel]:
        return self.db.query(AccountModel).filter(AccountModel.name == name).first()

    def list_all(self) -> List[AccountModel]:
        return self.db.query(AccountModel).all()

    def create(self, account: AccountModel) -> AccountModel:
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def delete(self, code: str) -> bool:
        account = self.get_by_code(code)
        if account:
            self.db.delete(account)
            self.db.commit()
            return True
        return False


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: str) -> Optional[DocumentModel]:
        return self.db.query(DocumentModel).filter(DocumentModel.id == id).first()

    def list_all(self, tenant_id: Optional[str] = None) -> List[DocumentModel]:
        query = self.db.query(DocumentModel)
        if tenant_id:
            query = query.filter(DocumentModel.tenant_id == tenant_id)
        return query.all()

    def create(self, document: DocumentModel) -> DocumentModel:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update(self, document: DocumentModel) -> DocumentModel:
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, id: str) -> bool:
        document = self.get_by_id(id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False


class JournalEntryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: str) -> Optional[JournalEntryModel]:
        return self.db.query(JournalEntryModel).filter(JournalEntryModel.id == id).first()

    def get_by_document_reference(self, document_reference: str) -> Optional[JournalEntryModel]:
        return self.db.query(JournalEntryModel).filter(JournalEntryModel.document_reference == document_reference).first()

    def list_all(self, tenant_id: Optional[str] = None) -> List[JournalEntryModel]:
        query = self.db.query(JournalEntryModel)
        if tenant_id:
            query = query.filter(JournalEntryModel.tenant_id == tenant_id)
        return query.all()

    def create(self, entry: JournalEntryModel) -> JournalEntryModel:
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete(self, id: str) -> bool:
        entry = self.get_by_id(id)
        if entry:
            self.db.delete(entry)
            self.db.commit()
            return True
        return False
