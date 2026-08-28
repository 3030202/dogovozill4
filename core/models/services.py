"""Paid Services Contract Model (ГК РФ гл. 39)."""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field
from core.models.base import BaseContract


class ServiceItem(BaseModel):
    """Specific service definition or deliverable."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Наименование услуги")
    description: Optional[str] = Field(None, description="Состав и описание оказываемых услуг")
    price: float = Field(..., gt=0, description="Стоимость услуги (руб.)")
    period_or_deadline: Optional[str] = Field(None, description="Срок или периодичность оказания")


class ServiceTerms(BaseModel):
    """Terms and condition for service execution and acceptance."""
    model_config = ConfigDict(extra="ignore")
    service_start_date: str = Field(..., description="Дата начала оказания услуг")
    service_end_date: str = Field(..., description="Дата окончания оказания услуг")
    act_review_days: int = Field(5, ge=1, description="Срок подписания Акта оказанных услуг или направления мотивированного отказа (дней)")
    ip_rights_transfer: bool = Field(True, description="Передача исключительных прав на результаты услуг Заказчику")


class ServiceContract(BaseContract):
    """Paid Services Contract per Russian Civil Code Chapter 39."""
    contract_type: str = Field("services", frozen=True)
    services: List[ServiceItem] = Field(default_factory=list, description="Перечень оказываемых услуг")
    service_terms: ServiceTerms

    @computed_field
    def total_amount(self) -> float:
        return round(sum(s.price for s in self.services), 2)
