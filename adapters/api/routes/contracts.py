"""API Routes for Contracts generation, calculation and validation."""

from __future__ import annotations
import io
from urllib.parse import quote
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from core.templates.registry import ContractRegistry, ContractTypeInfo
from core.validator import validate_party_requisites, validate_inn, validate_bik, suggest_party_by_inn
from core.rendering.docx_engine import DocxEngine
from core.rendering.typst_engine import TypstEngine
from core.rendering.libreoffice_engine import LibreOfficeEngine
from core.num_to_words import format_legal_contract_amount, format_rubles

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])


class ContractPayload(BaseModel):
    contract_type: str = Field(..., description="supply, services, work, nda")
    data: Dict[str, Any] = Field(..., description="Contract form data matching Pydantic schema")


class CalculationRequest(BaseModel):
    total_amount: float
    vat_rate: int = 20
    vat_included: bool = True
    is_exempt_vat: bool = False
    advance_percent: float = 0.0


@router.get("/types", response_model=List[ContractTypeInfo])
def get_contract_types():
    """List all available contract types."""
    return ContractRegistry.list_types()


@router.get("/schema/{contract_type}")
def get_contract_schema(contract_type: str):
    """Return JSONSchema for dynamic form generation."""
    try:
        model_cls = ContractRegistry.get_model_class(contract_type)
        return model_cls.model_json_schema()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sample/{contract_type}")
def get_sample_contract(contract_type: str):
    """Return realistic sample contract data with valid Russian requisites."""
    try:
        sample = ContractRegistry.get_sample_contract(contract_type)
        return sample.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/suggest/{inn}")
def suggest_party(inn: str):
    """Enrich party requisites by INN via DaData or return mathematical validation status."""
    return suggest_party_by_inn(inn)


@router.post("/validate-party")
def validate_party(party_data: Dict[str, Any]):
    """Validate Russian bank and tax requisites for a single party."""
    report = validate_party_requisites(party_data)
    return report


@router.post("/validate")
def validate_contract(payload: ContractPayload):
    """Validate full contract payload against Pydantic model and Russian legal rules."""
    try:
        contract = ContractRegistry.parse_contract(payload.contract_type, payload.data)
        # Also validate party requisites
        client_rep = validate_party_requisites(contract.client.model_dump())
        vendor_rep = validate_party_requisites(contract.vendor.model_dump())

        has_requisite_errors = (not client_rep["valid"]) or (not vendor_rep["valid"])

        return {
            "valid": True,
            "has_warnings": has_requisite_errors,
            "client_validation": client_rep,
            "vendor_validation": vendor_rep,
            "calculated_total": getattr(contract, "total_amount", 0.0),
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
        }


@router.post("/calculate")
def calculate_financials(req: CalculationRequest):
    """Calculate sums, VAT breakdown, and amount in Russian words."""
    legal_text = format_legal_contract_amount(
        total_amount=req.total_amount,
        vat_rate=req.vat_rate,
        vat_included=req.vat_included,
        is_exempt_vat=req.is_exempt_vat,
    )

    if req.is_exempt_vat or req.vat_rate == 0:
        vat_amount = 0.0
    elif req.vat_included:
        vat_amount = round(req.total_amount * req.vat_rate / (100 + req.vat_rate), 2)
    else:
        vat_amount = round(req.total_amount * req.vat_rate / 100, 2)

    advance_amount = round(req.total_amount * (req.advance_percent / 100.0), 2) if req.advance_percent else 0.0
    postpayment_amount = round(req.total_amount - advance_amount, 2)

    return {
        "total_amount": req.total_amount,
        "total_formatted": format_rubles(req.total_amount),
        "vat_amount": vat_amount,
        "vat_formatted": format_rubles(vat_amount),
        "advance_amount": advance_amount,
        "postpayment_amount": postpayment_amount,
        "legal_wording": legal_text,
    }


@router.post("/generate/docx")
def generate_docx(payload: ContractPayload):
    """Generate and download GOST-compliant DOCX document."""
    try:
        contract = ContractRegistry.parse_contract(payload.contract_type, payload.data)
        buffer = DocxEngine.generate(contract)
        filename = f"Contract_{payload.contract_type}_{contract.metadata.contract_number.replace('/', '_')}.docx"
        encoded_filename = quote(filename)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка генерации DOCX: {str(e)}")


@router.post("/generate/typst")
def generate_typst_source(payload: ContractPayload):
    """Generate Typst markup source code."""
    try:
        contract = ContractRegistry.parse_contract(payload.contract_type, payload.data)
        markup = TypstEngine.generate_typst_markup(contract)
        return Response(content=markup, media_type="text/plain; charset=utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка генерации Typst: {str(e)}")


@router.post("/generate/pdf")
def generate_pdf(payload: ContractPayload):
    """Generate PDF using Typst or LibreOffice fallback."""
    try:
        contract = ContractRegistry.parse_contract(payload.contract_type, payload.data)

        # Try Typst PDF compilation
        pdf_bytes = TypstEngine.compile_pdf(contract)
        # Check if bytes start with %PDF
        if pdf_bytes.startswith(b"%PDF"):
            filename = f"Contract_{payload.contract_type}_{contract.metadata.contract_number.replace('/', '_')}.pdf"
            encoded_filename = quote(filename)
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
            )

        # Fallback to LibreOffice if available
        docx_buf = DocxEngine.generate(contract)
        lo_pdf = LibreOfficeEngine.convert_docx_to_pdf(docx_buf.getvalue())
        if lo_pdf and lo_pdf.startswith(b"%PDF"):
            filename = f"Contract_{payload.contract_type}_{contract.metadata.contract_number.replace('/', '_')}.pdf"
            encoded_filename = quote(filename)
            return StreamingResponse(
                io.BytesIO(lo_pdf),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
            )

        # If PDF compiler not found, return Typst source code file with clear instructions
        filename = f"Contract_{payload.contract_type}_{contract.metadata.contract_number.replace('/', '_')}.typ"
        encoded_filename = quote(filename)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка генерации PDF: {str(e)}")
