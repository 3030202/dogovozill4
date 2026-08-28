"""Confidentiality Clauses for Standard Commercial Contracts."""

from __future__ import annotations
from typing import List, Dict, Any
from core.models.base import BaseContract
from core.models.nda import NDAContract


def build_confidentiality_clauses(contract: BaseContract) -> List[Dict[str, str]]:
    """Generate Section: Конфиденциальность."""
    if isinstance(contract, NDAContract):
        # NDA already has dedicated confidentiality terms in its core sections
        return []

    return [
        {
            "num": "6.1",
            "text": (
                "Стороны обязуются сохранять в тайне и не разглашать третьим лицам без предварительного письменного согласия другой Стороны "
                "любую информацию финансового, коммерческого или технического характера, полученную в связи с заключением и исполнением Договора."
            )
        },
        {
            "num": "6.2",
            "text": (
                "Обязательства по сохранению конфиденциальности сохраняют свою юридическую силу в течение всего срока действия настоящего Договора "
                "и в течение 3 (трех) лет после его прекращения или расторжения."
            )
        }
    ]
