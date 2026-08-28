"""Lease / Rental Contract Model (ГК РФ гл. 34, ст. 606-670)."""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field
from core.models.base import BaseContract


class LeaseObject(BaseModel):
    """Description of the leased property / equipment."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Наименование и характеристики имущества")
    inventory_number: Optional[str] = Field(None, description="Инвентарный / серийный номер")
    location: str = Field(..., description="Адрес (местонахождение) передаваемого имущества")
    condition: str = Field(
        "исправное, соответствующее целевому назначению",
        description="Техническое состояние на момент передачи"
    )
    market_value_rubles: Optional[float] = Field(
        None, ge=0, description="Рыночная/балансовая стоимость объекта (руб.) — для страхования и ответственности"
    )


class LeaseTerms(BaseModel):
    """Lease-specific terms."""
    model_config = ConfigDict(extra="ignore")

    rent_period_months: int = Field(12, ge=1, description="Срок аренды (месяцев)")
    monthly_rent_rubles: float = Field(..., gt=0, description="Ежемесячная арендная плата (руб.)")
    security_deposit_months: float = Field(
        1.0, ge=0, description="Размер обеспечительного платежа (в месячных арендных платежах)"
    )
    rent_change_notice_days: int = Field(
        30, ge=0, description="Срок уведомления об изменении арендной платы (дней)"
    )
    utilities_by_tenant: bool = Field(True, description="Коммунальные и эксплуатационные расходы на Арендаторе")
    repair_major_by_landlord: bool = Field(
        True, description="Капитальный ремонт — обязанность Арендодателя (ст. 616 ГК РФ)"
    )
    sublease_allowed: bool = Field(False, description="Субаренда разрешена")
    early_return_notice_days: int = Field(
        30, ge=0, description="Срок уведомления об досрочном возврате имущества (дней)"
    )


class LeaseContract(BaseContract):
    """Lease / Rental Contract per Russian Civil Code Chapter 34."""
    contract_type: str = Field("lease", frozen=True)
    lease_object: LeaseObject = Field(..., description="Объект аренды")
    lease_terms: LeaseTerms = Field(..., description="Условия аренды")

    @computed_field
    def total_amount(self) -> float:
        """Общая стоимость аренды за весь период."""
        return round(self.lease_terms.monthly_rent_rubles * self.lease_terms.rent_period_months, 2)
