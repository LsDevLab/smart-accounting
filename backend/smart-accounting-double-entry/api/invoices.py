from fastapi import APIRouter, UploadFile, File, HTTPException, status
from schemas.invoice_schema import InvoiceResponse
from schemas.double_entry_schema import DoubleEntryProposal

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])

@router.post("/process", response_model=DoubleEntryProposal, status_code=status.HTTP_202_ACCEPTED)
async def process_sdi_invoice(file: UploadFile = File(...)):
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="Formato non valido. Solo SDI XML consentiti.")

    return {
        "document_id": "SDI-2026-99812",
        "tenant_id": "COMPANY_A",
        "classification": "Fattura Ricevuta (Fornitore)",
        "account_mappings": [
            {"line_item": "Manutenzione climatizzatori uffici terzo piano", "account": "Spese di Manutenzione Immobili", "confidence": 0.96}
        ],
        "movements": [
            {"type": "DEBIT", "account": "Spese di Manutenzione Immobili", "amount": 1200.00},
            {"type": "CREDIT", "account": "Debiti verso Fornitori", "amount": 1200.00}
        ],
        "metadata": {"parsed_via": "SDI XML Parser v1", "ai_model": "SmartDE-Agent-v2"}
    }
