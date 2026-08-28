"""Supply Contract Model (ГК РФ гл. 30 §3)."""

from __future__ import annotations
from typing import List, Optional
from pydantic import Field, ConfigDict, computed_field
from core.models.base import BaseContract


class SupplyItem(BaseContract.model_config):
    """Specification item for supply goods."""
    name: str = Field(..., description="Наименование товара / артикул")
    unit: str = Field("шт.", description="Единица измерения (шт., компл., кг, м2 и т.д.)")
    quantity: float = Field(..., gt=0, description="Количество")
    price_per_unit: float = Field(..., gt=0, description="Цена за единицу (в рублях)")

    @computed_field
    def total_price(self) -> float:
        return round(self.quantity * self.price_per_unit, 2)


class DeliveryTerms(BaseContract.model_config):
    """Delivery terms and acceptance protocol."""
    method: str = Field(
        "vendor_delivery",
        description="vendor_delivery (доставка силами поставщика) / pickup (самовывоз) / carrier (транспортная компания)"
    )
    destination_address: str = Field(..., description="Адрес доставки / склад грузополучателя")
    delivery_timeframe_days: int = Field(10, ge=1, description="Срок поставки в рабочих днях с момента оплаты/заказа")
    acceptance_days: int = Field(3, ge=1, description="Срок приемки товара по количеству и качеству (дней)")
    packaging_requirements: Optional[str] = Field(
        "Товар должен быть упакован надлежащим образом, обеспечивающим сохранность при транспортировке",
        description="Требования к таре и упаковке"
    )


class SupplyContract(BaseContract):
    """Supply Contract per Russian Civil Code Chapter 30 §3."""
    contract_type: str = Field("supply", frozen=True)
    items: List[SupplyItem] = Field(default_factory=list, description="Спецификация поставляемых товаров")
    delivery_terms: DeliveryTerms = Field(
        default_factory=lambda: DeliveryTerms(
            destination_address="г. Москва, ул. Складская, д. 1"
        )
    )

    @computed_field
    def total_amount(self) -> float:
        return round(sum(item.total_price for item in self.items), 2)
