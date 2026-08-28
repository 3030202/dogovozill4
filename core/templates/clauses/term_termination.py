"""Term of Agreement and Termination Clauses (ГК РФ)."""

from __future__ import annotations
from typing import List, Dict, Any
from core.models.base import BaseContract
from core.models.nda import NDAContract


def build_term_termination_clauses(contract: BaseContract) -> List[Dict[str, str]]:
    """Generate Section: Срок действия и порядок расторжения Договора."""
    clauses = []

    if isinstance(contract, NDAContract):
        years = contract.nda_terms.confidentiality_years
        clauses.append({
            "num": "8.1",
            "text": (
                f"Настоящее Соглашение вступает в силу с даты его подписания обеими Сторонами и действует в течение {years} ({years}) лет."
            )
        })
        clauses.append({
            "num": "8.2",
            "text": (
                f"Обязательства по сохранению конфиденциальности остаются в силе в течение {years} лет после прекращения действия Соглашения."
            )
        })
        return clauses

    valid_until_str = contract.metadata.valid_until or "до полного исполнения Сторонами всех принятых на себя обязательств"
    clauses.append({
        "num": "8.1",
        "text": (
            f"Настоящий Договор вступает в силу с даты его подписания уполномоченными представителями обеих Сторон и действует {valid_until_str}."
        )
    })
    clauses.append({
        "num": "8.2",
        "text": (
            "Договор может быть изменен или расторгнут по взаимному соглашению Сторон, оформленному в виде дополнительного соглашения, "
            "подписанного обеими Сторонами."
        )
    })
    clauses.append({
        "num": "8.3",
        "text": (
            "Любая из Сторон вправе в одностороннем внесудебном порядке отказаться от исполнения Договора, "
            "письменно уведомив другую Сторону не менее чем за 30 (тридцать) календарных дней до предполагаемой даты расторжения, "
            "при условии проведения полных взаиморасчетов за фактически поставленный Товар / оказанные услуги / выполненные работы."
        )
    })

    if contract.additional_terms:
        clauses.append({
            "num": "8.4",
            "text": f"Особые условия: {contract.additional_terms}"
        })

    return clauses
