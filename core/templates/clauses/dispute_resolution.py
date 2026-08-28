"""Dispute Resolution and Jurisdiction Clauses (ГК РФ, АПК РФ)."""

from __future__ import annotations
from typing import List, Dict, Any
from core.models.base import BaseContract


def build_dispute_resolution_clauses(contract: BaseContract) -> List[Dict[str, str]]:
    """Generate Section: Порядок разрешения споров."""
    disp = contract.dispute_resolution

    jurisdiction_texts = {
        "arbitration_plaintiff": "в Арбитражном суде по месту нахождения Истца",
        "arbitration_defendant": "в Арбитражном суде по месту нахождения Ответчика",
        "moscow": "в Арбитражном суде города Москвы",
        "general": "в суде общей юрисдикции по месту нахождения Ответчика"
    }
    court_text = jurisdiction_texts.get(disp.court_jurisdiction, "в Арбитражном суде по месту нахождения Истца")

    return [
        {
            "num": "7.1",
            "text": (
                "Все споры, разногласия или требования, возникающие из настоящего Договора или в связи с ним, "
                "Стороны будут стремиться разрешить путем дружественных переговоров."
            )
        },
        {
            "num": "7.2",
            "text": (
                f"Соблюдение досудебного (претензионного) порядка урегулирования споров обязательно. "
                f"Срок рассмотрения письменной претензии и направления ответа на нее составляет "
                f"{disp.pre_trial_claim_days} ({disp.pre_trial_claim_days}) календарных дней со дня ее получения адресатом."
            )
        },
        {
            "num": "7.3",
            "text": (
                f"В случае невозможности разрешения спора в претензионном порядке, спор передается на рассмотрение "
                f"{court_text} в соответствии с процессуальным законодательством РФ."
            )
        }
    ]
