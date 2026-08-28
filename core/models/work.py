"""Work Contractor Contract Model (ГК РФ гл. 37)."""

from __future__ import annotations
from typing import List, Optional
from pydantic import Field, computed_field
from core.models.base import BaseContract


class WorkStage(BaseContract.model_config):
    """Stage in contractor work plan."""
    stage_number: int = Field(..., ge=1, description="Номер этапа")
    title: str = Field(..., description="Наименование этапа работ")
    start_date: str = Field(..., description="Дата начала этапа")
    end_date: str = Field(..., description="Дата завершения этапа")
    cost: float = Field(..., gt=0, description="Стоимость этапа (руб.)")
    deliverable_result: Optional[str] = Field(None, description="Овеществленный результат этапа работ")


class WorkTerms(BaseContract.model_config):
    """Terms for work execution, warranty and acceptance."""
    materials_by_contractor: bool = Field(True, description="Работы выполняются иждивением подрядчика (из его материалов)")
    warranty_months: int = Field(12, ge=0, description="Гарантийный срок на результат работ (месяцев)")
    acceptance_days: int = Field(5, ge=1, description="Срок приемки выполненных работ по Акту КС-2 / Акту приемки (дней)")
    subcontracting_allowed: bool = Field(True, description="Право подрядчика привлекать субподрядчиков")


class WorkContract(BaseContract):
    """Work Contractor Contract per Russian Civil Code Chapter 37."""
    contract_type: str = Field("work", frozen=True)
    work_object_name: str = Field(..., description="Объект выполнения работ (напр. Офисное помещение, Информационная система)")
    work_location: str = Field(..., description="Место выполнения работ")
    stages: List[WorkStage] = Field(default_factory=list, description="Этапы и календарный план работ")
    work_terms: WorkTerms = Field(default_factory=WorkTerms)

    @computed_field
    def total_amount(self) -> float:
        return round(sum(stage.cost for stage in self.stages), 2)
