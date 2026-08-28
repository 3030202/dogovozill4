"""Payment and Cost Clauses for Russian Civil Contracts."""

from __future__ import annotations
from typing import List, Dict, Any
from core.num_to_words import format_legal_contract_amount, format_rubles
from core.models.base import BaseContract


def build_payment_clauses(contract: BaseContract) -> List[Dict[str, str]]:
    """Generate Section 2: Цена договора и порядок расчетов."""
    clauses = []
    total_amount = getattr(contract, "total_amount", 0.0)

    if total_amount > 0:
        price_wording = format_legal_contract_amount(
            total_amount=total_amount,
            vat_rate=contract.vat_rate,
            vat_included=contract.vat_included,
            is_exempt_vat=contract.is_exempt_vat
        )
        clauses.append({
            "num": "2.1",
            "text": f"Общая цена настоящего Договора составляет: {price_wording}."
        })
    else:
        clauses.append({
            "num": "2.1",
            "text": "Настоящее Соглашение является безвозмездным и не предполагает взаимных финансовых расчетов между Сторонами."
        })
        return clauses

    # Payment mode
    payment = contract.payment_terms
    days_noun = "банковских (рабочих)" if payment.days_type == "banking" else "календарных"

    if payment.type == "100_PREPAYMENT":
        clauses.append({
            "num": "2.2",
            "text": (
                "Оплата производится в форме 100% (стопроцентной) предварительной оплаты "
                f"в течение {payment.postpayment_days} ({payment.postpayment_days}) {days_noun} дней "
                "с даты выставления счета Исполнителем / Поставщиком."
            )
        })
    elif payment.type == "50_50":
        advance_rate = payment.advance_percent or 50.0
        post_rate = 100.0 - advance_rate
        advance_amount = round(total_amount * (advance_rate / 100.0), 2)
        post_amount = round(total_amount - advance_amount, 2)
        clauses.append({
            "num": "2.2",
            "text": (
                f"Оплата осуществляется в два этапа: авансовый платеж в размере {advance_rate:g}% ({format_rubles(advance_amount)} руб.) "
                f"выплачивается в течение 3 (трех) банковских дней с момента подписания Договора, "
                f"а оставшиеся {post_rate:g}% ({format_rubles(post_amount)} руб.) — в течение {payment.postpayment_days} {days_noun} дней "
                "после подписания итогового двустороннего Акта / УПД."
            )
        })
    else:
        clauses.append({
            "num": "2.2",
            "text": (
                f"Оплата производится в полном объеме в течение {payment.postpayment_days} ({payment.postpayment_days}) {days_noun} дней "
                "с момента подписания Сторонами товарной накладной / Акта оказанных услуг / УПД."
            )
        })

    clauses.append({
        "num": "2.3",
        "text": (
            "Все расчеты по настоящему Договору производятся в безналичном порядке в валюте Российской Федерации (рубли РФ) "
            "путем перечисления денежных средств на расчетный счет Стороны, указанный в разделе «Реквизиты и подписи Сторон»."
        )
    })
    clauses.append({
        "num": "2.4",
        "text": (
            "Обязательство по оплате считается исполненным с момента списания денежных средств с расчетного счета плательщика "
            "либо зачисления на корреспондентский счет банка получателя."
        )
    })

    return clauses
