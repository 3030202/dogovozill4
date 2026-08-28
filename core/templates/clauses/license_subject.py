"""Subject and Special Clauses for Software License / SaaS Agreement (ГК РФ ч. IV)."""

from __future__ import annotations
from typing import List, Dict, Any
from core.models.license_sw import LicenseSWContract, LicenseType


def build_license_subject_clauses(contract: LicenseSWContract) -> List[Dict[str, str]]:
    """Section 1 — Предмет лицензионного договора."""
    lt = contract.license_terms
    sw_list = contract.software

    license_type_text = {
        LicenseType.SIMPLE: "простую (неисключительную) лицензию (ст. 1236 ч. 1 ГК РФ)",
        LicenseType.EXCLUSIVE: "исключительную лицензию (ст. 1236 ч. 2 ГК РФ)",
        LicenseType.SUBLICENSE: "сублицензию (ст. 1238 ГК РФ)",
    }.get(lt.license_type, "простую лицензию")

    sw_names = "; ".join(
        f"{sw.name}" + (f" (v{sw.version})" if sw.version else "")
        for sw in sw_list
    ) or "Программное обеспечение (далее — ПО)"

    period_text = (
        f"на срок {lt.period_months} ({lt.period_months}) месяцев"
        if lt.period_months
        else "на неопределенный срок (бессрочно)"
    )

    territory_text = lt.territory

    clauses = [
        {
            "num": "1.1",
            "text": (
                f"Лицензиар предоставляет Лицензиату {license_type_text} на использование "
                f"следующего программного обеспечения: {sw_names}, {period_text}, "
                f"на территории: {territory_text}."
            )
        },
        {
            "num": "1.2",
            "text": (
                "Право использования ПО предоставляется следующими способами, прямо предусмотренными настоящим Договором: "
                "воспроизведение (инсталляция и запуск), хранение в памяти технических средств, "
                + ("модификация (адаптация) ПО; " if lt.modification_allowed else "")
                + ("передача сублицензии; " if lt.sublicense_allowed else "")
                + f"предоставление доступа через сеть Интернет ({lt.period_months} мес.)."
                if lt.period_months else "предоставление доступа через сеть Интернет."
            )
        },
    ]

    if lt.allowed_users:
        clauses.append({
            "num": "1.3",
            "text": (
                f"Лицензиат вправе предоставить доступ к ПО не более чем {lt.allowed_users} "
                f"({lt.allowed_users}) авторизованным пользователям одновременно."
            )
        })

    if not lt.source_code_included:
        clauses.append({
            "num": "1.4",
            "text": (
                "Исходный код ПО не передается Лицензиату. Декомпиляция, дизассемблирование и иная попытка "
                "извлечения исходного кода ПО без письменного согласия Лицензиара запрещены."
            )
        })

    if lt.sla_uptime_percent is not None:
        clauses.append({
            "num": "1.5",
            "text": (
                f"Лицензиар гарантирует доступность SaaS-сервиса не менее {lt.sla_uptime_percent}% "
                "времени в месяц (SLA). При недоступности сверх допустимого порога Лицензиар предоставляет "
                "компенсацию в виде продления срока лицензии."
            )
        })

    if lt.support_included:
        clauses.append({
            "num": "1.6",
            "text": (
                f"В стоимость лицензионного вознаграждения включена техническая поддержка. "
                f"Срок реакции на обращение: не более {lt.support_response_hours} часов в рабочие дни."
            )
        })

    return clauses
