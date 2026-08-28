"""Liability and Penalties Clauses (ГК РФ)."""

from __future__ import annotations
from typing import List, Dict, Any
from core.num_to_words import format_rubles
from core.models.base import BaseContract
from core.models.nda import NDAContract


def build_liability_clauses(contract: BaseContract) -> List[Dict[str, str]]:
    """Generate Section 4: Ответственность Сторон."""
    clauses = []
    penalties = contract.penalty_terms

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

    # Standard Commercial contract liability
    if penalties.use_cbr_key_rate:
        penalty_desc = "в размере 1/300 ключевой ставки Центрального банка РФ"
    else:
        penalty_desc = f"в размере {penalties.penalty_rate_daily}%"

    clauses.append({
        "num": "4.1",
        "text": (
            "За неисполнение или ненадлежащее исполнение обязательств по настоящему Договору Стороны несут ответственность "
            "в соответствии с действующим законодательством Российской Федерации."
        )
    })

    clauses.append({
        "num": "4.2",
        "text": (
            f"В случае нарушения Заказчиком / Покупателем сроков оплаты, Исполнитель / Поставщик вправе потребовать уплаты пени "
            f"{penalty_desc} от не уплаченной в срок суммы за каждый календарный день просрочки, "
            f"но не более {penalties.max_penalty_percent}% от общей суммы задолженности."
        )
    })

    clauses.append({
        "num": "4.3",
        "text": (
            f"В случае нарушения Исполнителем / Поставщиком сроков выполнения работ / оказания услуг / поставки Товара, "
            f"Заказчик / Покупатель вправе потребовать уплаты пени {penalty_desc} от стоимости не поставленного в срок Товара "
            f"(не оказанных услуг) за каждый календарный день просрочки, но не более {penalties.max_penalty_percent}%."
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
