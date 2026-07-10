from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.account_schema import AccountCreate, AccountUpdate, AccountResponse
from application.account_service import AccountApplicationService
from api.dependencies import get_account_service

router = APIRouter(prefix="/api/accounts", tags=["Piano dei Conti"])

@router.get("", response_model=List[AccountResponse])
def get_all_accounts(
    service: Annotated[AccountApplicationService, Depends(get_account_service)]
):
    return service.list_all()

@router.get("/{code}", response_model=AccountResponse)
def get_account(
    code: str,
    service: Annotated[AccountApplicationService, Depends(get_account_service)]
):
    account = service.get_by_code(code)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with code {code} not found"
        )
    return account

@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    schema: AccountCreate,
    service: Annotated[AccountApplicationService, Depends(get_account_service)]
):
    existing = service.get_by_code(schema.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account with code {schema.code} already exists"
        )
    return service.create(schema)

@router.patch("/{code}", response_model=AccountResponse)
def update_account(
    code: str,
    schema: AccountUpdate,
    service: Annotated[AccountApplicationService, Depends(get_account_service)]
):
    account = service.update(code, schema)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with code {code} not found"
        )
    return account

@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    code: str,
    service: Annotated[AccountApplicationService, Depends(get_account_service)]
):
    deleted = service.delete(code)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with code {code} not found"
        )
    return None
