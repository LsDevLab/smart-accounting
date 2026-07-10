from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from schemas.double_entry_schema import JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse
from application.double_entry_service import DoubleEntryApplicationService
from api.dependencies import get_double_entry_service
from domain.exceptions import UnbalancedEntryException, InvalidAccountMappingException

router = APIRouter(prefix="/api/double-entry/movements", tags=["Double Entry Movements"])

@router.get("", response_model=List[JournalEntryResponse])
def get_all_movements(
    service: Annotated[DoubleEntryApplicationService, Depends(get_double_entry_service)],
    tenant_id: Optional[str] = None
):
    return service.list_all(tenant_id)

@router.get("/{id}", response_model=JournalEntryResponse)
def get_movement(
    id: str,
    service: Annotated[DoubleEntryApplicationService, Depends(get_double_entry_service)]
):
    entry = service.get_by_id(id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal entry with ID {id} not found"
        )
    return entry

@router.post("", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_movement(
    schema: JournalEntryCreate,
    service: Annotated[DoubleEntryApplicationService, Depends(get_double_entry_service)]
):
    existing = service.get_by_id(schema.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Journal entry with ID {schema.id} already exists"
        )
    try:
        return service.create_manual_entry(schema)
    except (UnbalancedEntryException, InvalidAccountMappingException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{id}", response_model=JournalEntryResponse)
def update_movement(
    id: str,
    schema: JournalEntryUpdate,
    service: Annotated[DoubleEntryApplicationService, Depends(get_double_entry_service)]
):
    try:
        entry = service.update_manual_entry(id, schema)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Journal entry with ID {id} not found"
            )
        return entry
    except (UnbalancedEntryException, InvalidAccountMappingException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movement(
    id: str,
    service: Annotated[DoubleEntryApplicationService, Depends(get_double_entry_service)]
):
    deleted = service.delete(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal entry with ID {id} not found"
        )
    return None
