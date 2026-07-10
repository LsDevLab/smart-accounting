from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from schemas.document_schema import DocumentCreate, DocumentUpdate, DocumentResponse
from application.document_service import DocumentApplicationService
from api.dependencies import get_document_service
from domain.exceptions import InvalidAccountMappingException, UnbalancedEntryException

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.get("", response_model=List[DocumentResponse])
def get_all_documents(
    service: Annotated[DocumentApplicationService, Depends(get_document_service)],
    tenant_id: Optional[str] = None
):
    return service.list_all(tenant_id)

@router.get("/{id}", response_model=DocumentResponse)
def get_document(
    id: str,
    service: Annotated[DocumentApplicationService, Depends(get_document_service)]
):
    doc = service.get_by_id(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {id} not found"
        )
    return doc

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    schema: DocumentCreate,
    service: Annotated[DocumentApplicationService, Depends(get_document_service)]
):
    existing = service.get_by_id(schema.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document with ID {schema.id} already exists"
        )
    try:
        return service.create(schema)
    except InvalidAccountMappingException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UnbalancedEntryException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{id}", response_model=DocumentResponse)
def update_document(
    id: str,
    schema: DocumentUpdate,
    service: Annotated[DocumentApplicationService, Depends(get_document_service)]
):
    try:
        doc = service.update(id, schema)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {id} not found"
            )
        return doc
    except InvalidAccountMappingException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UnbalancedEntryException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    id: str,
    service: Annotated[DocumentApplicationService, Depends(get_document_service)]
):
    deleted = service.delete(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {id} not found"
        )
    return None
