"""Software License / SaaS Agreement Model (ГК РФ ч. IV, ст. 1235-1238)."""

from __future__ import annotations
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, computed_field
from core.models.base import BaseContract


class LicenseType(str, Enum):
    """Вид лицензии."""
    SIMPLE = "SIMPLE"          # Простая (неисключительная) лицензия — ст. 1236 ГК РФ ч.1
    EXCLUSIVE = "EXCLUSIVE"    # Исключительная лицензия — ст. 1236 ГК РФ ч.2
    SUBLICENSE = "SUBLICENSE"  # Сублицензионный договор — ст. 1238 ГК РФ


class SoftwareDeliverable(BaseModel):
    """Description of the licensed software / module."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Наименование программного обеспечения / модуля")
    version: Optional[str] = Field(None, description="Версия ПО")
    registration_number: Optional[str] = Field(
        None, description="Номер свидетельства о гос. регистрации программы для ЭВМ (Роспатент)"
    )
    delivery_method: str = Field(
        "облачный доступ (SaaS)",
        description="Способ передачи: облачный доступ (SaaS), скачивание, физический носитель"
    )


class LicenseTerms(BaseModel):
    """License-specific terms."""
    model_config = ConfigDict(extra="ignore")

    license_type: LicenseType = Field(LicenseType.SIMPLE, description="Вид лицензии")
    territory: str = Field("Российская Федерация", description="Территория действия лицензии")
    period_months: Optional[int] = Field(
        12, ge=1, description="Срок лицензии (месяцев). None = бессрочная"
    )
    allowed_users: Optional[int] = Field(
        None, ge=1, description="Максимальное число пользователей. None = без ограничений"
    )
    allowed_installations: Optional[int] = Field(
        None, ge=1, description="Максимальное число установок. None = без ограничений"
    )
    source_code_included: bool = Field(False, description="Передача исходного кода")
    modification_allowed: bool = Field(False, description="Право на модификацию ПО")
    sublicense_allowed: bool = Field(False, description="Право на передачу сублицензий")
    sla_uptime_percent: Optional[float] = Field(
        99.0, ge=0, le=100, description="Гарантируемый SLA доступности сервиса (%)"
    )
    support_included: bool = Field(True, description="Техническая поддержка включена в лицензию")
    support_response_hours: int = Field(24, ge=1, description="Срок ответа техподдержки (часов)")


class LicenseSWContract(BaseContract):
    """Software / SaaS License Agreement per Russian Civil Code Part IV."""
    contract_type: str = Field("license_sw", frozen=True)
    software: List[SoftwareDeliverable] = Field(
        default_factory=list, description="Перечень лицензируемого ПО"
    )
    license_terms: LicenseTerms = Field(default_factory=LicenseTerms)
    license_fee: float = Field(..., gt=0, description="Лицензионное вознаграждение (руб.)")
    fee_type: str = Field(
        "единовременно",
        description="Порядок выплаты: единовременно / ежемесячно / ежегодно / роялти"
    )

    @computed_field
    def total_amount(self) -> float:
        return round(self.license_fee, 2)
