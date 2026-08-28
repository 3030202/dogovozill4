"""Base Pydantic v2 Models for Deterministic Russian Legal Contracts."""

from __future__ import annotations
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from core.validator import validate_inn, validate_kpp, validate_ogrn, validate_bik, validate_bank_account
from core.models.stance import LegalStance


class PartyType(str, Enum):
    OOO = "OOO"                    # ООО (Общество с ограниченной ответственностью)
    AO = "AO"                      # АО / ПАО (Акционерное общество)
    IP = "IP"                      # ИП (Индивидуальный предприниматель)
    SELF_EMPLOYED = "SELF_EMPLOYED"# Самозанятый (Плательщик НПД)
    INDIVIDUAL = "INDIVIDUAL"      # Физическое лицо


class BankRequisites(BaseModel):
    """Russian Bank details."""
    model_config = ConfigDict(extra="ignore")

    bik: str = Field(..., description="9-значный БИК банка")
    bank_name: str = Field(..., description="Наименование банка (напр., ПАО СБЕРБАНК)")
    account: str = Field(..., description="20-значный расчетный счет")
    corr_account: Optional[str] = Field(None, description="20-значный корреспондентский счет")

    @field_validator("bik")
    @classmethod
    def check_bik(cls, v: str) -> str:
        v_clean = v.strip()
        ok, msg = validate_bik(v_clean)
        if not ok:
            raise ValueError(msg)
        return v_clean


class Party(BaseModel):
    """Legal entity or individual details for contract parties."""
    model_config = ConfigDict(extra="ignore")

    party_type: PartyType = Field(PartyType.OOO, description="Организационно-правовая форма")
    full_name: str = Field(..., description="Полное фирменное наименование или ФИО")
    short_name: Optional[str] = Field(None, description="Сокращенное наименование")
    inn: str = Field(..., description="ИНН (10 или 12 цифр)")
    kpp: Optional[str] = Field(None, description="КПП (для юридических лиц)")
    ogrn: Optional[str] = Field(None, description="ОГРН (13 цифр) или ОГРНИП (15 цифр)")
    legal_address: str = Field(..., description="Юридический адрес")
    actual_address: Optional[str] = Field(None, description="Фактический / почтовый адрес")
    signatory_position: str = Field("Генеральный директор", description="Должность подписанта")
    signatory_name: str = Field(..., description="ФИО подписанта (напр., Иванов Иван Иванович)")
    signatory_basis: str = Field("Устава", description="Основание полномочий (Устава, доверенности №...)")
    bank_requisites: BankRequisites = Field(..., description="Банковские реквизиты")
    phone: Optional[str] = Field(None, description="Контактный телефон")
    email: Optional[str] = Field(None, description="Электронная почта")

    @field_validator("inn")
    @classmethod
    def check_inn(cls, v: str) -> str:
        v_clean = v.strip()
        ok, msg = validate_inn(v_clean)
        if not ok:
            raise ValueError(msg)
        return v_clean


class PaymentTerms(BaseModel):
    """Payment schedule and conditions."""
    model_config = ConfigDict(extra="ignore")

    type: str = Field("100_POSTPAYMENT", description="100_PREPAYMENT, 50_50, 100_POSTPAYMENT, CUSTOM")
    advance_percent: float = Field(0.0, ge=0.0, le=100.0, description="Процент аванса (0-100)")
    postpayment_days: int = Field(5, ge=1, description="Срок окончательного расчета (в днях)")
    days_type: str = Field("banking", description="banking (банковских) или calendar (календарных) дней")
    description: Optional[str] = Field(None, description="Пользовательское описание условий оплаты")


class PenaltyTerms(BaseModel):
    """Penalties and late payment interest."""
    model_config = ConfigDict(extra="ignore")

    penalty_rate_daily: float = Field(0.1, ge=0.0, description="Размер неустойки (% в день от суммы просрочки)")
    max_penalty_percent: float = Field(10.0, ge=0.0, le=100.0, description="Максимальный размер неустойки (%)")
    use_cbr_key_rate: bool = Field(False, description="Использовать 1/300 ключевой ставки ЦБ РФ вместо фиксированного %")
    fine_fixed_amount: float = Field(0.0, ge=0.0, description="Штраф за неисполнение неденежных обязательств (руб.)")


class DisputeResolution(BaseModel):
    """Pre-trial claim protocol and court jurisdiction."""
    model_config = ConfigDict(extra="ignore")

    pre_trial_claim_days: int = Field(30, ge=0, description="Срок ответа на досудебную претензию (календарных дней)")
    court_jurisdiction: str = Field("arbitration_plaintiff", description="Подсудность: arbitration_plaintiff / arbitration_defendant / moscow / general")


class ContractMetadata(BaseModel):
    """Contract header and identification."""
    model_config = ConfigDict(extra="ignore")

    contract_number: str = Field(..., description="Номер договора")
    contract_date: str = Field(..., description="Дата заключения (ГГГГ-ММ-ДД или ДД.ММ.ГГГГ)")
    city: str = Field("г. Москва", description="Место заключения договора")
    valid_until: Optional[str] = Field(None, description="Срок действия договора")


class BaseContract(BaseModel):
    """Root model for all deterministic contracts."""
    model_config = ConfigDict(extra="ignore")

    metadata: ContractMetadata
    client: Party = Field(..., description="Сторона 1 (Заказчик / Покупатель / Заказчик)")
    vendor: Party = Field(..., description="Сторона 2 (Исполнитель / Поставщик / Подрядчик)")
    payment_terms: PaymentTerms = Field(default_factory=PaymentTerms)
    penalty_terms: PenaltyTerms = Field(default_factory=PenaltyTerms)
    dispute_resolution: DisputeResolution = Field(default_factory=DisputeResolution)
    vat_rate: int = Field(20, description="Ставка НДС (20, 10, 0)")
    vat_included: bool = Field(True, description="НДС включен в цену")
    is_exempt_vat: bool = Field(False, description="Освобожден от НДС (УСН / ст. 346.11 НК РФ)")
    legal_stance: LegalStance = Field(
        LegalStance.BALANCED,
        description="Юридическая позиция: PRO_BUYER (защита Заказчика), BALANCED (нейтрально), PRO_VENDOR (защита Исполнителя)"
    )
    additional_terms: Optional[str] = Field(None, description="Дополнительные особые условия")
