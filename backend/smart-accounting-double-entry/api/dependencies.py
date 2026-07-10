from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.database import get_db
from application.account_service import AccountApplicationService
from application.document_service import DocumentApplicationService
from application.double_entry_service import DoubleEntryApplicationService

def get_account_service(
    db: Annotated[Session, Depends(get_db)]
) -> AccountApplicationService:
    return AccountApplicationService(db)

def get_document_service(
    db: Annotated[Session, Depends(get_db)]
) -> DocumentApplicationService:
    return DocumentApplicationService(db)

def get_double_entry_service(
    db: Annotated[Session, Depends(get_db)]
) -> DoubleEntryApplicationService:
    return DoubleEntryApplicationService(db)
