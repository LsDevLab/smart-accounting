from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# Existing proposal schemas (retained for backward compatibility)
class AccountMappingDTO(BaseModel):
    line_item: str
    account: str
    confidence: float

class MovementDTO(BaseModel):
    type: str
    account: str
    amount: float

class DoubleEntryProposal(BaseModel):
    document_id: str
    tenant_id: str
    classification: str
    account_mappings: List[AccountMappingDTO]
    movements: List[MovementDTO]
    metadata: dict


# CRUD schemas for Double Entry Movements (Journal Entries and Lines)
class DoubleEntryLineCreate(BaseModel):
    account_code: str
    is_debit: bool
    amount: float = Field(..., gt=0)

class DoubleEntryLineUpdate(BaseModel):
    account_code: str
    is_debit: bool
    amount: float = Field(..., gt=0)

class DoubleEntryLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    journal_entry_id: str
    account_code: str
    is_debit: bool
    amount: float

class JournalEntryCreate(BaseModel):
    id: str
    tenant_id: str
    entry_date: datetime
    document_reference: Optional[str] = None
    movements: List[DoubleEntryLineCreate]

class JournalEntryUpdate(BaseModel):
    entry_date: Optional[datetime] = None
    document_reference: Optional[str] = None
    movements: Optional[List[DoubleEntryLineCreate]] = None

class JournalEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    tenant_id: str
    entry_date: datetime
    document_reference: Optional[str] = None
    lines: List[DoubleEntryLineResponse]
