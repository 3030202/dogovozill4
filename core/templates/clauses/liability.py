"""Liability and Penalties Clauses (ГК РФ) — with LegalStance support."""

from __future__ import annotations
from typing import List, Dict, Any
from core.num_to_words import format_rubles
from core.models.base import BaseContract
from core.models.nda import NDAContract
from core.models.stance import LegalStance


def build_liability_clauses(contract: BaseContract) -> List[Dict[str, str]]:
    """Generate Section 4: Ответственность Сторон с учетом правовой позиции."""
    clauses = []
    penalties = contract.penalty_terms
    stance = contract.legal_stance

    if isinstance(contract, NDAContract):
        fine_amount = contract.nda_terms.disclosure_penalty_rubles
        clauses.append({
            "num": "4.1",
            "text": (
                "За каждый установленный факт несанкционированного раскрытия или нецелевого использования Конфиденциальной информации "
                f"виновная Сторона выплачивает потерпевшей Стороне штраф в размере {format_rubles(fine_amount)} "
                "рублей, а также возмещает причиненные реальные документально подтвержденные убытки в полном объеме."
            )
        })
        clauses.append({
            "num": "4.2",
            "text": (
                "Уплата штрафа не освобождает виновную Сторону от обязанности прекратить неправомерное использование информации "
                "и уничтожить все незаконно изготовленные копии."
            )
        })
        return clauses

    clauses.append({
        "num": "4.1",
        "text": (
            "За неисполнение или ненадлежащее исполнение обязательств по настоящему Договору Стороны несут ответственность "
            "в соответствии с действующим законодательством Российской Федерации."
        )
    })

    # --- Пени Заказчика за просрочку оплаты ---
    # PRO_VENDOR: мягкие пени, потолок 5% (защищает Заказчика от Исполнителя)
    # PRO_BUYER: жёсткие пени на Заказчика (защищает Исполнителя от недоплаты)
    if stance == LegalStance.PRO_VENDOR:
        buyer_penalty_desc = "в размере 1/300 ключевой ставки Центрального банка РФ"
        buyer_penalty_cap = "5%"
    elif stance == LegalStance.PRO_BUYER:
        buyer_penalty_desc = "в размере 0,5% (ноль целых пять десятых процента)"
        buyer_penalty_cap = None  # без ограничения потолка
    else:  # BALANCED
        if penalties.use_cbr_key_rate:
            buyer_penalty_desc = "в размере 1/300 ключевой ставки Центрального банка РФ"
        else:
            buyer_penalty_desc = f"в размере {penalties.penalty_rate_daily}%"
        buyer_penalty_cap = f"{penalties.max_penalty_percent}%"

    buyer_cap_text = (
        f", но не более {buyer_penalty_cap} от общей суммы задолженности"
        if buyer_penalty_cap else ""
    )
    clauses.append({
        "num": "4.2",
        "text": (
            f"В случае нарушения Заказчиком / Покупателем сроков оплаты, Исполнитель / Поставщик вправе потребовать "
            f"уплаты пени {buyer_penalty_desc} от не уплаченной в срок суммы за каждый календарный день просрочки"
            f"{buyer_cap_text}."
        )
    })

    # --- Пени Исполнителя за просрочку исполнения ---
    # PRO_BUYER: жёсткие пени Исполнителя, нет потолка (защищает Заказчика)
    # PRO_VENDOR: мягкие пени, потолок 5%
    if stance == LegalStance.PRO_BUYER:
        vendor_penalty_desc = "в размере 0,5% (ноль целых пять десятых процента)"
        vendor_penalty_cap = None
    elif stance == LegalStance.PRO_VENDOR:
        vendor_penalty_desc = "в размере 1/300 ключевой ставки Центрального банка РФ"
        vendor_penalty_cap = "5%"
    else:  # BALANCED
        if penalties.use_cbr_key_rate:
            vendor_penalty_desc = "в размере 1/300 ключевой ставки Центрального банка РФ"
        else:
            vendor_penalty_desc = f"в размере {penalties.penalty_rate_daily}%"
        vendor_penalty_cap = f"{penalties.max_penalty_percent}%"

    vendor_cap_text = (
        f", но не более {vendor_penalty_cap} от стоимости не поставленного в срок Товара (не оказанных услуг)"
        if vendor_penalty_cap else ""
    )
    clauses.append({
        "num": "4.3",
        "text": (
            f"В случае нарушения Исполнителем / Поставщиком сроков выполнения работ / оказания услуг / поставки Товара, "
            f"Заказчик / Покупатель вправе потребовать уплаты пени {vendor_penalty_desc} "
            f"от стоимости просроченного обязательства за каждый календарный день просрочки{vendor_cap_text}."
        )
    })

    if penalties.fine_fixed_amount > 0:
        clauses.append({
            "num": "4.4",
            "text": (
                f"За нарушение иных неденежных обязательств виновная Сторона уплачивает другой Стороне фиксированный штраф "
                f"в размере {format_rubles(penalties.fine_fixed_amount)} рублей за каждый доказанный факт нарушения."
            )
        })

    return clauses
