"""Unit tests for Russian amount to words and VAT breakdown generator."""

import pytest
from core.num_to_words import (
    number_to_words_ru,
    amount_to_words_ru,
    format_rubles,
    format_legal_contract_amount,
)


class TestNumberToWords:
    def test_zero(self):
        assert number_to_words_ru(0) == "ноль"

    def test_simple_units(self):
        assert number_to_words_ru(1) == "один"
        assert number_to_words_ru(5) == "пять"
        assert number_to_words_ru(12) == "двенадцать"
        assert number_to_words_ru(42) == "сорок два"

    def test_thousands_and_millions(self):
        assert number_to_words_ru(1000) == "одна тысяча"
        assert number_to_words_ru(2000) == "две тысячи"
        assert number_to_words_ru(5000) == "пять тысяч"
        assert number_to_words_ru(125400) == "сто двадцать пять тысяч четыреста"
        assert number_to_words_ru(1000000) == "один миллион"


class TestAmountToWords:
    def test_amount_with_kopecks(self):
        res = amount_to_words_ru(125400.50)
        assert res == "Сто двадцать пять тысяч четыреста рублей 50 копеек"

    def test_amount_single_ruble(self):
        res = amount_to_words_ru(1.01)
        assert res == "Один рубль 01 копейка"

    def test_amount_few_rubles(self):
        res = amount_to_words_ru(2.02)
        assert res == "Два рубля 02 копейки"


class TestFormatRubles:
    def test_currency_formatting(self):
        assert format_rubles(125400) == "125 400,00"
        assert format_rubles(1500000.50) == "1 500 000,50"


class TestLegalContractAmount:
    def test_vat_20_included(self):
        res = format_legal_contract_amount(120000.00, vat_rate=20, vat_included=True)
        assert "120 000,00 (Сто двадцать тысяч) рублей 00 копеек" in res
        assert "в том числе НДС 20% в размере 20 000,00" in res

    def test_vat_exempt_usn(self):
        res = format_legal_contract_amount(100000.00, is_exempt_vat=True)
        assert "100 000,00 (Сто тысяч) рублей 00 копеек" in res
        assert "НДС не облагается" in res
