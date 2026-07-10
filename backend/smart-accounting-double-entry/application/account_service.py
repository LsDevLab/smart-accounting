from typing import List, Optional
from sqlalchemy.orm import Session
from models.account_model import AccountModel
from infrastructure.repositories import AccountRepository
from schemas.account_schema import AccountCreate, AccountUpdate

class AccountApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AccountRepository(db)

    def get_by_code(self, code: str) -> Optional[AccountModel]:
        return self.repo.get_by_code(code)

    def list_all(self) -> List[AccountModel]:
        accounts = self.repo.list_all()
        if not accounts:
            self.seed_default_accounts()
            accounts = self.repo.list_all()
        return accounts

    def create(self, schema: AccountCreate) -> AccountModel:
        model = AccountModel(
            code=schema.code,
            name=schema.name,
            account_type=schema.account_type.value
        )
        return self.repo.create(model)

    def update(self, code: str, schema: AccountUpdate) -> Optional[AccountModel]:
        model = self.repo.get_by_code(code)
        if not model:
            return None
        model.name = schema.name
        model.account_type = schema.account_type.value
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete(self, code: str) -> bool:
        return self.repo.delete(code)

    def seed_default_accounts(self):
        defaults = [
            ("600001", "Spese di Manutenzione Immobili", "COSTO"),
            ("600002", "Spese di Cancelleria", "COSTO"),
            ("600003", "Costo Energia Elettrica", "COSTO"),
            ("600004", "Acquisto Materie Prime", "COSTO"),
            ("500001", "Vendita di Servizi", "RICAVO"),
            ("500002", "Vendita di Prodotti", "RICAVO"),
            ("110001", "Crediti verso Clienti", "ATTIVO"),
            ("450001", "Debiti verso Fornitori", "PASSIVO"),
            ("220001", "IVA a Credito", "ATTIVO"),
            ("220002", "IVA a Debito", "PASSIVO"),
        ]
        for code, name, type_ in defaults:
            if not self.repo.get_by_code(code):
                acc = AccountModel(code=code, name=name, account_type=type_)
                self.repo.create(acc)
