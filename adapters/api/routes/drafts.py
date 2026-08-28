"""API Routes for Drafts management."""

from __future__ import annotations
import os
import json
import uuid
import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/drafts", tags=["Drafts"])

DRAFTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage/drafts"))
os.makedirs(DRAFTS_DIR, exist_ok=True)


class DraftCreateRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    contract_type: str
    data: Dict[str, Any]


class DraftSummary(BaseModel):
    id: str
    title: str
    contract_type: str
    updated_at: float
    updated_at_formatted: str
    client_name: Optional[str] = None
    vendor_name: Optional[str] = None


@router.post("")
def save_draft(req: DraftCreateRequest):
    """Save or update contract draft."""
    draft_id = req.id or str(uuid.uuid4())
    filename = f"draft_{draft_id}.json"
    filepath = os.path.join(DRAFTS_DIR, filename)

    now = time.time()
    payload = {
        "id": draft_id,
        "title": req.title or f"Черновик от {time.strftime('%d.%m.%Y %H:%M', time.localtime(now))}",
        "contract_type": req.contract_type,
        "data": req.data,
        "created_at": now,
        "updated_at": now,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return {"status": "saved", "id": draft_id, "title": payload["title"]}


@router.get("", response_model=List[DraftSummary])
def list_drafts():
    """List all saved drafts."""
    results = []
    if not os.path.exists(DRAFTS_DIR):
        return []

    for filename in sorted(os.listdir(DRAFTS_DIR), reverse=True):
        if filename.endswith(".json"):
            filepath = os.path.join(DRAFTS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    client = data.get("data", {}).get("client", {}).get("full_name")
                    vendor = data.get("data", {}).get("vendor", {}).get("full_name")
                    upd = data.get("updated_at", os.path.getmtime(filepath))
                    results.append(
                        DraftSummary(
                            id=data.get("id", filename.replace(".json", "")),
                            title=data.get("title", filename),
                            contract_type=data.get("contract_type", "supply"),
                            updated_at=upd,
                            updated_at_formatted=time.strftime("%d.%m.%Y %H:%M", time.localtime(upd)),
                            client_name=client,
                            vendor_name=vendor,
                        )
                    )
            except Exception:
                continue

    return results


@router.get("/{draft_id}")
def get_draft(draft_id: str):
    """Retrieve draft content by ID."""
    clean_id = draft_id.replace("draft_", "").replace(".json", "")
    filepath = os.path.join(DRAFTS_DIR, f"draft_{clean_id}.json")
    if not os.path.exists(filepath):
        # try exact filename
        filepath = os.path.join(DRAFTS_DIR, f"{draft_id}.json")
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Черновик не найден")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@router.delete("/{draft_id}")
def delete_draft(draft_id: str):
    """Delete draft by ID."""
    clean_id = draft_id.replace("draft_", "").replace(".json", "")
    filepath = os.path.join(DRAFTS_DIR, f"draft_{clean_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "deleted", "id": draft_id}
    raise HTTPException(status_code=404, detail="Черновик не найден")
