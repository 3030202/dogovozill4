"""Non-Disclosure Agreement Model (NDA / Соглашение о конфиденциальности)."""

from __future__ import annotations
from typing import Optional, List
from pydantic import Field
from core.models.base import BaseContract


class NDAScope(BaseContract.model_config):
    """Scope of protected confidential information."""
    purpose: str = Field(
        "Оценка возможности заключения и исполнение коммерческих сделок между Сторонами",
        description="Цель раскрытия информации"
    )
    confidential_scope: List[str] = Field(
        default_factory=lambda: [
            "Техническая и технологическая информация (исходные коды, архитектура, спецификации)",
            "Коммерческая и финансовая информация (бизнес-планы, цены, условия договоров, клиенты)",
            "Организационная и кадровая структура, персональные данные сотрудников",
            "Любая иная информация с грифом 'Коммерческая тайна' или 'Конфиденциально'"
        ],
        description="Перечень категорий конфиденциальной информации"
    )
    marking_required: bool = Field(False, description="Требуется ли обязательный письменный гриф 'Конфиденциально'")


class NDATerms(BaseContract.model_config):
    """Protection period and liability."""
    is_bilateral: bool = Field(True, description="Двустороннее обязательство о неразглашении")
    confidentiality_years: int = Field(3, ge=1, description="Срок охраны конфиденциальности после раскрытия (лет)")
    disclosure_penalty_rubles: float = Field(500000.0, ge=0, description="Штраф за факт разглашения (руб.)")


class NDAContract(BaseContract):
    """Non-Disclosure Agreement."""
    contract_type: str = Field("nda", frozen=True)
    scope: NDAScope = Field(default_factory=NDAScope)
    nda_terms: NDATerms = Field(default_factory=NDATerms)
