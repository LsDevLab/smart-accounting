from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class DocumentType(str, Enum):
    ENTRATA = "ENTRATA"
    USCITA = "USCITA"

class DocumentCreate(BaseModel):
    id: str
    tenant_id: str
    description: str
    amount: float = Field(..., gt=0)
    vat_rate: float = Field(0.22, ge=0)
    sender_vat: Optional[str] = None
    receiver_vat: Optional[str] = None
    document_type: DocumentType

class DocumentUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    vat_rate: Optional[float] = Field(None, ge=0)
    sender_vat: Optional[str] = None
    receiver_vat: Optional[str] = None
    document_type: Optional[DocumentType] = None
    status: Optional[str] = None
    mapped_account_code: Optional[str] = None

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    tenant_id: str
    description: str
    amount: float
    vat_rate: float
    sender_vat: Optional[str] = None
    receiver_vat: Optional[str] = None
    document_type: DocumentType
    created_at: datetime
    status: str
    mapped_account_code: Optional[str] = None
