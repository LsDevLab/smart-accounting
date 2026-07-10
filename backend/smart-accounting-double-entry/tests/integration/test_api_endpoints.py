import pytest

# Helper to verify a movement DTO
def check_movement(movements, code, is_debit, amount):
    line = next((m for m in movements if m["account_code"] == code and m["is_debit"] == is_debit), None)
    assert line is not None
    assert abs(line["amount"] - amount) < 1e-6

def test_api_accounts_crud(client):
    # 1. Get seeded accounts
    response = client.get("/api/accounts")
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) > 0

    # 2. Create new account
    payload = {
        "code": "999888",
        "name": "Acquisto Macchinari Ufficio",
        "account_type": "COSTO"
    }
    response = client.post("/api/accounts", json=payload)
    assert response.status_code == 201
    assert response.json()["code"] == "999888"

    # 3. Read specific account
    response = client.get("/api/accounts/999888")
    assert response.status_code == 200
    assert response.json()["name"] == "Acquisto Macchinari Ufficio"

    # 4. Patch account
    patch_payload = {
        "name": "Costo Acquisto Macchinari Ufficio",
        "account_type": "COSTO"
    }
    response = client.patch("/api/accounts/999888", json=patch_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Costo Acquisto Macchinari Ufficio"

    # 5. Delete account
    response = client.delete("/api/accounts/999888")
    assert response.status_code == 204

    # 6. Read deleted account -> 404
    response = client.get("/api/accounts/999888")
    assert response.status_code == 404

def test_api_documents_and_movements_lifecycle(client):
    # 1. Seeding: triggering account list seeds accounts
    client.get("/api/accounts")

    # 2. Create document (USCITA/Purchase Invoice)
    # Description contains "cancelleria", which maps to 600002 (Spese di Cancelleria)
    doc_payload = {
        "id": "DOC-API-01",
        "tenant_id": "TENANT-1",
        "description": "Acquisto carta stampante e cancelleria varia",
        "amount": 244.0,
        "vat_rate": 0.22,
        "sender_vat": "IT11111111111",
        "receiver_vat": "IT22222222222",
        "document_type": "USCITA"
    }
    response = client.post("/api/documents", json=doc_payload)
    assert response.status_code == 201
    doc_res = response.json()
    assert doc_res["id"] == "DOC-API-01"
    assert doc_res["status"] == "COMPLETED"
    assert doc_res["mapped_account_code"] == "600002"

    # 3. Verify double-entry movement was generated automatically
    response = client.get("/api/double-entry/movements")
    assert response.status_code == 200
    movements = response.json()
    assert len(movements) == 1
    
    je = movements[0]
    assert je["id"] == "JE-DOC-API-01"
    assert je["document_reference"] == "DOC-API-01"
    assert len(je["lines"]) == 3
    
    # Debits: 600002 (200.00), 220001 (44.00)
    # Credit: 450001 (244.00)
    check_movement(je["lines"], "600002", True, 200.00)
    check_movement(je["lines"], "220001", True, 44.00)
    check_movement(je["lines"], "450001", False, 244.00)

    # 4. Patch document: change description and amount
    # Description "energia elettrica" maps to 600003
    patch_payload = {
        "description": "Bolletta Energia Elettrica maggio",
        "amount": 122.0
    }
    response = client.patch("/api/documents/DOC-API-01", json=patch_payload)
    assert response.status_code == 200
    doc_res_updated = response.json()
    assert doc_res_updated["mapped_account_code"] == "600003"
    assert doc_res_updated["amount"] == 122.0

    # 5. Verify movements were updated correctly
    response = client.get("/api/double-entry/movements/JE-DOC-API-01")
    assert response.status_code == 200
    je_updated = response.json()
    assert len(je_updated["lines"]) == 3
    
    # Debits: 600003 (100.00), 220001 (22.00)
    # Credit: 450001 (122.00)
    check_movement(je_updated["lines"], "600003", True, 100.00)
    check_movement(je_updated["lines"], "220001", True, 22.00)
    check_movement(je_updated["lines"], "450001", False, 122.00)

    # 6. Delete document
    response = client.delete("/api/documents/DOC-API-01")
    assert response.status_code == 204

    # 7. Verify document and movements are gone
    response = client.get("/api/documents/DOC-API-01")
    assert response.status_code == 404
    response = client.get("/api/double-entry/movements/JE-DOC-API-01")
    assert response.status_code == 404

def test_api_manual_double_entry_crud(client):
    # Seed accounts
    client.get("/api/accounts")

    # 1. Create a manual double entry
    # Debit 110001 (Crediti verso Clienti): 500.00
    # Credit 500001 (Vendita di Servizi): 500.00
    payload = {
        "id": "JE-MANUAL-01",
        "tenant_id": "TENANT-1",
        "entry_date": "2026-07-10T21:00:00",
        "document_reference": "MANUAL-REF-99",
        "movements": [
            {"account_code": "110001", "is_debit": True, "amount": 500.0},
            {"account_code": "500001", "is_debit": False, "amount": 500.0}
        ]
    }
    response = client.post("/api/double-entry/movements", json=payload)
    assert response.status_code == 201
    res = response.json()
    assert res["id"] == "JE-MANUAL-01"
    assert len(res["lines"]) == 2

    # Try creating an unbalanced entry (should fail)
    bad_payload = {
        "id": "JE-BAD-01",
        "tenant_id": "TENANT-1",
        "entry_date": "2026-07-10T21:00:00",
        "movements": [
            {"account_code": "110001", "is_debit": True, "amount": 500.0},
            {"account_code": "500001", "is_debit": False, "amount": 490.0}
        ]
    }
    response = client.post("/api/double-entry/movements", json=bad_payload)
    assert response.status_code == 400
