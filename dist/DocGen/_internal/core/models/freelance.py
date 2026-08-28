"""Freelance / Self-Employed (ГПХ) Contract Model (ГК РФ гл. 39, ФЗ № 422-ФЗ «О НПД»)."""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field
from core.models.base import BaseContract


class FreelanceTask(BaseModel):
    """A specific task or deliverable in a freelance contract."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Наименование задачи / результата")
    description: Optional[str] = Field(None, description="Подробное описание требований")
    cost: float = Field(..., gt=0, description="Стоимость выполнения задачи (руб.)")
    deadline_days: Optional[int] = Field(None, ge=1, description="Срок выполнения (рабочих дней)")


class FreelanceTerms(BaseModel):
    """Terms specific to freelance / self-employed contracts."""
    model_config = ConfigDict(extra="ignore")

    is_self_employed: bool = Field(
        True, description="Исполнитель — самозанятый (плательщик НПД по ФЗ № 422-ФЗ)"
    )
    self_employed_inn: Optional[str] = Field(
        None, description="ИНН самозанятого (совпадает с полем INN стороны)"
    )
    check_receipt_required: bool = Field(
        True, description="Исполнитель обязан предоставить чек из приложения «Мой налог»"
    )
    ip_rights_transfer: bool = Field(
        True, description="Права на результаты интеллектуальной деятельности переходят к Заказчику"
    )
    no_employment_relations: bool = Field(
        True, description="Договор не является трудовым, не создает отношений работника и работодателя (ст. 15 ТК РФ)"
    )
    act_review_days: int = Field(3, ge=1, description="Срок подписания Акта приемки работ (рабочих дней)")
    guaranteed_min_amount: Optional[float] = Field(
        None, ge=0, description="Гарантированный минимальный объем заказа (руб.)"
    )


class FreelanceContract(BaseContract):
    """Contract of Civil Nature (ГПХ) with Freelancer / Self-employed person."""
    contract_type: str = Field("freelance", frozen=True)
    tasks: List[FreelanceTask] = Field(default_factory=list, description="Перечень заданий и результатов")
    freelance_terms: FreelanceTerms = Field(default_factory=FreelanceTerms)

    @computed_field
    def total_amount(self) -> float:
        return round(sum(t.cost for t in self.tasks), 2)
