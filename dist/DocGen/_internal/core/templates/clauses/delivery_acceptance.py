"""Delivery and Acceptance Clauses (ГК РФ) — with LegalStance support."""

from __future__ import annotations
from typing import List, Dict, Any
from core.models.supply import SupplyContract
from core.models.services import ServiceContract
from core.models.work import WorkContract
from core.models.nda import NDAContract
from core.models.stance import LegalStance


def build_delivery_acceptance_clauses(contract: Any) -> List[Dict[str, str]]:
    """Generate Section 3: Порядок поставки / сдачи-приемки / исполнения."""
    clauses = []

    if isinstance(contract, SupplyContract):
        terms = contract.delivery_terms
        clauses.append({
            "num": "3.1",
            "text": (
                f"Поставка Товара осуществляется по адресу: {terms.destination_address} "
                f"в течение {terms.delivery_timeframe_days} рабочих дней с момента перечисления оплаты / согласования заявки."
            )
        })
        clauses.append({
            "num": "3.2",
            "text": (
                f"Приемка Товара по количеству и качеству производится Покупателем в течение {terms.acceptance_days} "
                "рабочих дней с момента получения Товара. Право собственности и риск случайной гибели переходят к Покупателю "
                "с момента подписания товарной накладной (ТОРГ-12) или Универсального передаточного документа (УПД)."
            )
        })
        clauses.append({
            "num": "3.3",
            "text": (
                f"Требования к упаковке: {terms.packaging_requirements}."
            )
        })

    elif isinstance(contract, ServiceContract):
        terms = contract.service_terms
        clauses.append({
            "num": "3.1",
            "text": (
                "По факту оказания услуг Исполнитель составляет и направляет Заказчику двусторонний Акт оказанных услуг (или УПД) "
                "в 2 (двух) экземплярах либо через систему юридически значимого электронного документооборота (ЭДО)."
            )
        })
        # Срок молчаливой приемки зависит от правовой позиции
        stance = contract.legal_stance
        if stance == LegalStance.PRO_VENDOR:
            silent_days = 3
        elif stance == LegalStance.PRO_BUYER:
            silent_days = 7
        else:
            silent_days = terms.act_review_days

        clauses.append({
            "num": "3.2",
            "text": (
                f"Заказчик обязан в течение {silent_days} рабочих дней со дня получения Акта подписать его и направить один экземпляр "
                "Исполнителю либо представить мотивированный письменный отказ от приемки с указанием перечня необходимых доработок."
            )
        })
        clauses.append({
            "num": "3.3",
            "text": (
                f"В случае если в течение {silent_days} рабочих дней Заказчик не направил подписанный Акт или мотивированный отказ, "
                "услуги считаются оказанными в полном объеме, с надлежащим качеством и принятыми Заказчиком без замечаний."
            )
        })

    elif isinstance(contract, WorkContract):
        terms = contract.work_terms
        clauses.append({
            "num": "3.1",
            "text": (
                "Подрядчик выполняет работы в соответствии с этапами Календарного плана. "
                "По завершении каждого этапа (или всего объема работ) Подрядчик письменно уведомляет Заказчика и передает Акт приемки выполненных работ (форма КС-2, КС-3 или УПД)."
            )
        })
        clauses.append({
            "num": "3.2",
            "text": (
                f"Заказчик обязан с участием Подрядчика осмотреть и принять результат работ в течение {terms.acceptance_days} рабочих дней "
                "либо направить перечень замечаний с указанием разумных сроков их безвозмездного устранения Подрядчиком."
            )
        })
        clauses.append({
            "num": "3.3",
            "text": (
                "Скрытые работы подлежат освидетельствованию с составлением соответствующих актов промежуточной приемки до начала последующих работ."
            )
        })

    elif isinstance(contract, NDAContract):
        clauses.append({
            "num": "3.1",
            "text": (
                "Передача Конфиденциальной информации осуществляется по защищенным каналам связи, на физических носителях по актам приема-передачи "
                "либо путем предоставления ограниченного авторизованного доступа к информационным системам."
            )
        })
        clauses.append({
            "num": "3.2",
            "text": (
                "Получающая сторона обязана соблюдать степень заботливости и осмотрительности не меньшую, чем в отношении собственной конфиденциальной информации "
                "высокой ценности, и допускать к информации только тех сотрудников, которым она необходима для реализации установленной Цели."
            )
        })

    return clauses
