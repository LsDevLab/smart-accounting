from pydantic import BaseModel, ConfigDict
from enum import Enum

class AccountType(str, Enum):
    COSTO = "COSTO"
    RICAVO = "RICAVO"
    ATTIVO = "ATTIVO"
    PASSIVO = "PASSIVO"

class AccountCreate(BaseModel):
    code: str
    name: str
    account_type: AccountType

class AccountUpdate(BaseModel):
    name: str
    account_type: AccountType

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    code: str
    name: str
    account_type: AccountType
