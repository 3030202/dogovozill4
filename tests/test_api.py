"""Unit tests for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from adapters.api.server import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_contract_types():
    response = client.get("/api/contracts/types")
    assert response.status_code == 200
    types = response.json()
    assert len(types) == 4
    keys = [t["key"] for t in types]
    assert "supply" in keys
    assert "services" in keys
    assert "work" in keys
    assert "nda" in keys


def test_get_sample_contract():
    response = client.get("/api/contracts/sample/supply")
    assert response.status_code == 200
    data = response.json()
    assert data["contract_type"] == "supply"
    assert "metadata" in data
    assert "client" in data
    assert "vendor" in data


def test_calculate_financials():
    payload = {
        "total_amount": 120000.0,
        "vat_rate": 20,
        "vat_included": True,
        "is_exempt_vat": False,
        "advance_percent": 50.0,
    }
    response = client.post("/api/contracts/calculate", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["total_amount"] == 120000.0
    assert res["vat_amount"] == 20000.0
    assert res["advance_amount"] == 60000.0
    assert "Сто двадцать тысяч" in res["legal_wording"]


def test_validate_party_endpoint():
    payload = {
        "inn": "7707083893",
        "bank_requisites": {
            "bik": "044525225",
            "account": "40702810938000012345",
        }
    }
    response = client.post("/api/contracts/validate-party", json=payload)
    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_generate_docx_endpoint():
    sample_res = client.get("/api/contracts/sample/supply")
    sample_data = sample_res.json()

    gen_res = client.post(
        "/api/contracts/generate/docx",
        json={"contract_type": "supply", "data": sample_data}
    )
    assert gen_res.status_code == 200
    assert "application/vnd.openxmlformats-officedocument" in gen_res.headers["content-type"]
    assert len(gen_res.content) > 10000


def test_drafts_crud():
    # 1. Create draft
    draft_payload = {
        "title": "Тестовый черновик",
        "contract_type": "supply",
        "data": {"test": "data"},
    }
    create_res = client.post("/api/drafts", json=draft_payload)
    assert create_res.status_code == 200
    draft_id = create_res.json()["id"]

    # 2. Get draft
    get_res = client.get(f"/api/drafts/{draft_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Тестовый черновик"

    # 3. List drafts
    list_res = client.get("/api/drafts")
    assert list_res.status_code == 200
    assert any(d["id"] == draft_id for d in list_res.json())

    # 4. Delete draft
    del_res = client.delete(f"/api/drafts/{draft_id}")
    assert del_res.status_code == 200
