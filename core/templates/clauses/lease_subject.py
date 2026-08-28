"""Subject and Special Clauses for Lease Contract (ГК РФ гл. 34)."""

from __future__ import annotations
from typing import List, Dict, Any
from core.num_to_words import format_rubles
from core.models.lease import LeaseContract


def build_lease_subject_clauses(contract: LeaseContract) -> List[Dict[str, str]]:
    """Section 1 — Предмет договора аренды."""
    obj = contract.lease_object
    terms = contract.lease_terms

    clauses = [
        {
            "num": "1.1",
            "text": (
                f"Арендодатель обязуется предоставить Арендатору во временное возмездное пользование "
                f"следующее имущество: {obj.name}. "
                + (f"Инвентарный / серийный номер: {obj.inventory_number}. " if obj.inventory_number else "")
                + f"Местонахождение имущества: {obj.location}."
            )
        },
        {
            "num": "1.2",
            "text": (
                f"Техническое состояние имущества на момент передачи: {obj.condition}. "
                "Факт передачи имущества оформляется двусторонним Актом приема-передачи."
            )
        },
    ]

    if obj.market_value_rubles:
        clauses.append({
            "num": "1.3",
            "text": (
                f"Рыночная стоимость передаваемого имущества составляет {format_rubles(obj.market_value_rubles)} рублей. "
                "Арендатор несет ответственность за сохранность имущества в пределах указанной стоимости."
            )
        })

    return clauses


def build_lease_terms_clauses(contract: LeaseContract) -> List[Dict[str, str]]:
    """Section (inline) — Условия пользования и возврата имущества."""
    terms = contract.lease_terms
    clauses = []

    # Обеспечительный платеж
    if terms.security_deposit_months > 0:
        deposit_amount = round(terms.monthly_rent_rubles * terms.security_deposit_months, 2)
        clauses.append({
            "num": "3.4",
            "text": (
                f"Арендатор в течение 5 рабочих дней с даты подписания Договора перечисляет Арендодателю "
                f"обеспечительный (гарантийный) платеж в размере {format_rubles(deposit_amount)} рублей "
                f"({terms.security_deposit_months} ежемесячных платежей). Обеспечительный платеж возвращается Арендатору "
                f"не позднее 10 рабочих дней после возврата имущества в надлежащем состоянии."
            )
        })

    # Субаренда
    sublease_text = (
        "Арендатор вправе с письменного согласия Арендодателя передавать имущество в субаренду третьим лицам."
        if terms.sublease_allowed
        else "Передача имущества в субаренду, а равно передача прав по Договору третьим лицам без письменного согласия Арендодателя запрещена."
    )
    clauses.append({"num": "3.5", "text": sublease_text})

    # Коммунальные платежи
    if terms.utilities_by_tenant:
        clauses.append({
            "num": "3.6",
            "text": (
                "Коммунальные, эксплуатационные и иные расходы по содержанию имущества несет Арендатор "
                "и оплачивает их самостоятельно по отдельным договорам с ресурсоснабжающими организациями "
                "или возмещает Арендодателю на основании выставленных счетов."
            )
        })

    # Ремонт
    if terms.repair_major_by_landlord:
        clauses.append({
            "num": "3.7",
            "text": (
                "Капитальный ремонт имущества производится Арендодателем за его счет в сроки, согласованные "
                "Сторонами в письменной форме (ст. 616 ГК РФ). Текущий ремонт, поддержание имущества в исправном "
                "состоянии — обязанность Арендатора."
            )
        })

    return clauses
