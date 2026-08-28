"""Subject Clauses for Supply, Services, Work and NDA contracts (ГК РФ)."""

from __future__ import annotations
from typing import List, Dict, Any
from core.models.supply import SupplyContract
from core.models.services import ServiceContract
from core.models.work import WorkContract
from core.models.nda import NDAContract


def build_subject_clauses(contract: Any) -> List[Dict[str, str]]:
    """Build numbered sub-paragraphs for Section 1: Предмет договора."""
    clauses = []

    if isinstance(contract, SupplyContract):
        clauses.append({
            "num": "1.1",
            "text": (
                "Поставщик обязуется поставить и передать в собственность Покупателя, "
                "а Покупатель обязуется принять и оплатить Товар в количестве, ассортименте, "
                "комплектности и по ценам, указанным в Спецификации (Приложение № 1 к настоящему Договору), "
                "являющейся неотъемлемой частью Договора."
            )
        })
        clauses.append({
            "num": "1.2",
            "text": (
                "Поставляемый Товар должен быть новым, не бывшим в употреблении, свободным от любых прав "
                "и притязаний третьих лиц, не состоять в споре и под арестом."
            )
        })
        clauses.append({
            "num": "1.3",
            "text": (
                "Качество Товара должно полностью соответствовать действующим ГОСТ, ТУ производителя "
                "и подтверждаться соответствующими сертификатами и паспортами качества."
            )
        })

    elif isinstance(contract, ServiceContract):
        services_list = ", ".join(f"«{s.name}»" for s in contract.services) if contract.services else "согласно Приложению"
        clauses.append({
            "num": "1.1",
            "text": (
                f"Исполнитель обязуется по заданию Заказчика оказать комплекс возмездных услуг: {services_list}, "
                "а Заказчик обязуется принять и оплатить оказанные услуги в порядке и на условиях, предусмотренных настоящим Договором."
            )
        })
        clauses.append({
            "num": "1.2",
            "text": (
                f"Срок оказания услуг: с «{contract.service_terms.service_start_date}» по «{contract.service_terms.service_end_date}» включительно."
            )
        })
        if contract.service_terms.ip_rights_transfer:
            clauses.append({
                "num": "1.3",
                "text": (
                    "Исключительные права на все результаты интеллектуальной деятельности, созданные Исполнителем "
                    "в процессе оказания услуг по настоящему Договору, переходят к Заказчику в полном объеме с момента подписания Акта оказанных услуг."
                )
            })

    elif isinstance(contract, WorkContract):
        clauses.append({
            "num": "1.1",
            "text": (
                f"Подрядчик обязуется по заданию Заказчика выполнить комплекс подрядных работ на объекте: «{contract.work_object_name}» "
                f"(расположенном по адресу: {contract.work_location}) и сдать их результат Заказчику, "
                "а Заказчик обязуется создать Подрядчику необходимые условия, принять результат работ и оплатить его обусловленную цену."
            )
        })
        mat_text = "иждивением Подрядчика (из его материалов, его силами и средствами)" if contract.work_terms.materials_by_contractor else "из материалов Заказчика"
        clauses.append({
            "num": "1.2",
            "text": f"Работы выполняются {mat_text} в строгом соответствии с Календарным планом (Приложение № 1) и действующими СНиП и ГОСТ."
        })
        clauses.append({
            "num": "1.3",
            "text": (
                f"Гарантийный срок на выполненные Подрядчиком работы составляет {contract.work_terms.warranty_months} месяцев "
                "со дня подписания Сторонами итогового Акта приемки выполненных работ."
            )
        })

    elif isinstance(contract, NDAContract):
        clauses.append({
            "num": "1.1",
            "text": (
                f"Настоящее Соглашение регулирует отношения Сторон по передаче, использованию и охране конфиденциальной информации "
                f"в связи с реализацией следующей цели: {contract.scope.purpose}."
            )
        })
        scope_items = "; ".join(contract.scope.confidential_scope)
        clauses.append({
            "num": "1.2",
            "text": (
                f"Под «Конфиденциальной информацией» Стороны понимают любые сведения, составляющие коммерческую, техническую, "
                f"технологическую, финансовую тайну, включая: {scope_items}."
            )
        })
        marking_text = "в обязательном порядке содержит письменный гриф «Конфиденциально» или «Коммерческая тайна»" if contract.scope.marking_required else "передается в любой форме (письменной, устной, электронной) без обязательного нанесения грифа конфиденциальности"
        clauses.append({
            "num": "1.3",
            "text": f"Конфиденциальной признается информация, которая {marking_text}."
        })

    return clauses
