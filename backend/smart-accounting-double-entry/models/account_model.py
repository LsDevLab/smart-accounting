from sqlalchemy import Column, String
from infrastructure.database import Base

class AccountModel(Base):
    __tablename__ = "accounts"
    code = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    account_type = Column(String, nullable=False) # e.g. COSTO, RICAVO, ATTIVO, PASSIVO
