"""Dispute Resolution and Jurisdiction Clauses (ГК РФ, АПК РФ) — with LegalStance support."""

from __future__ import annotations
from typing import List, Dict, Any
from core.models.base import BaseContract
from core.models.stance import LegalStance


def build_dispute_resolution_clauses(contract: BaseContract) -> List[Dict[str, str]]:
    """Generate Section: Порядок разрешения споров с учетом правовой позиции."""
    disp = contract.dispute_resolution
    stance = contract.legal_stance

    # Выбор суда по умолчанию из поля dispute_resolution
    explicit_map = {
        "arbitration_plaintiff": "в Арбитражном суде по месту нахождения Истца",
        "arbitration_defendant": "в Арбитражном суде по месту нахождения Ответчика",
        "moscow": "в Арбитражном суде города Москвы",
        "general": "в суде общей юрисдикции по месту нахождения Ответчика",
    }

    # Если пользователь явно задал нестандартную подсудность — уважаем её
    if disp.court_jurisdiction in ("moscow", "general"):
        court_text = explicit_map[disp.court_jurisdiction]
    else:
        # Stance override для arbitration случаев
        if stance == LegalStance.PRO_BUYER:
            court_text = "в Арбитражном суде по месту нахождения Заказчика"
        elif stance == LegalStance.PRO_VENDOR:
            court_text = "в Арбитражном суде по месту нахождения Исполнителя / Поставщика"
        else:  # BALANCED — по месту Истца (нейтрально)
            court_text = explicit_map.get(disp.court_jurisdiction, "в Арбитражном суде по месту нахождения Истца")

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
