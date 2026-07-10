from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class InvoiceType(str, Enum):
    ENTRATA = "ENTRATA"
    USCITA = "USCITA"

class InvoiceCreate(BaseModel):
    id: str
    tenant_id: str
    description: str
    amount: float = Field(..., gt=0)
    vat_rate: float = Field(0.22, ge=0)
    sender_vat: Optional[str] = None
    receiver_vat: Optional[str] = None
    document_type: InvoiceType

class InvoiceUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    vat_rate: Optional[float] = Field(None, ge=0)
    sender_vat: Optional[str] = None
    receiver_vat: Optional[str] = None
    document_type: Optional[InvoiceType] = None
    status: Optional[str] = None
    mapped_account: Optional[str] = None

class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    tenant_id: str
    description: str
    amount: float
    vat_rate: float
    sender_vat: Optional[str] = None
    receiver_vat: Optional[str] = None
    document_type: InvoiceType
    created_at: datetime
    status: str
    mapped_account: Optional[str] = None
