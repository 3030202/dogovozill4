"""DocGen Core Package."""

from core.validator import (
    validate_inn,
    validate_kpp,
    validate_ogrn,
    validate_bik,
    validate_bank_account,
    validate_party_requisites,
    suggest_party_by_inn,
)
from core.num_to_words import (
    number_to_words_ru,
    amount_to_words_ru,
    format_rubles,
    format_legal_contract_amount,
)
from core.templates.registry import ContractRegistry
from core.rendering import DocxEngine, TypstEngine, LibreOfficeEngine

__all__ = [
    "validate_inn",
    "validate_kpp",
    "validate_ogrn",
    "validate_bik",
    "validate_bank_account",
    "validate_party_requisites",
    "number_to_words_ru",
    "amount_to_words_ru",
    "format_rubles",
    "format_legal_contract_amount",
    "ContractRegistry",
    "DocxEngine",
    "TypstEngine",
    "LibreOfficeEngine",
]
