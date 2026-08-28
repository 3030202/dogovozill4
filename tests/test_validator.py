"""Unit tests for Russian legal and banking requisites validators."""

import pytest
from core.validator import (
    validate_inn,
    validate_kpp,
    validate_ogrn,
    validate_bik,
    validate_bank_account,
    validate_party_requisites,
    suggest_party_by_inn,
)


class TestInnValidation:
    def test_valid_legal_entity_10_digits(self):
        # Sberbank INN
        ok, msg = validate_inn("7707083893")
        assert ok is True
        assert "корректен" in msg

    def test_invalid_legal_entity_checksum(self):
        ok, msg = validate_inn("7707083890")
        assert ok is False
        assert "Неверная контрольная сумма" in msg

    def test_valid_individual_12_digits(self):
        # Valid 12-digit INN
        ok, msg = validate_inn("500100732259")
        assert ok is True
        assert "корректен" in msg

    def test_invalid_individual_checksum(self):
        ok, msg = validate_inn("500100732250")
        assert ok is False

    def test_invalid_length(self):
        ok, msg = validate_inn("12345")
        assert ok is False
        assert "10 или 12 цифр" in msg

    def test_empty_inn(self):
        ok, msg = validate_inn("")
        assert ok is False
        assert "не может быть пустым" in msg


class TestKppValidation:
    def test_valid_kpp(self):
        ok, msg = validate_kpp("770701001")
        assert ok is True

    def test_empty_kpp_is_allowed(self):
        # KPP is optional for IP and individuals
        ok, msg = validate_kpp(None)
        assert ok is True
        ok, msg = validate_kpp("")
        assert ok is True

    def test_invalid_length_kpp(self):
        ok, msg = validate_kpp("770701")
        assert ok is False


class TestOgrnValidation:
    def test_valid_ogrn_13_digits(self):
        # Sberbank OGRN
        ok, msg = validate_ogrn("1027700132195")
        assert ok is True

    def test_invalid_ogrn_checksum(self):
        ok, msg = validate_ogrn("1027700132190")
        assert ok is False

    def test_valid_ogrnip_15_digits(self):
        ok, msg = validate_ogrn("304500116000157")
        assert ok is True

    def test_invalid_ogrnip_checksum(self):
        ok, msg = validate_ogrn("304500116000150")
        assert ok is False


class TestBikAndAccountValidation:
    def test_valid_bik(self):
        ok, msg = validate_bik("044525225")
        assert ok is True

    def test_invalid_bik_non_04(self):
        ok, msg = validate_bik("123456789")
        assert ok is False
        assert "начинаться с 04" in msg

    def test_valid_account_with_bik(self):
        bik = "044525225"
        acc = "40702810938000012345"
        ok, msg = validate_bank_account(acc, bik)
        assert ok is True

    def test_invalid_account_checksum(self):
        bik = "044525225"
        acc = "40702810038000012345"
        ok, msg = validate_bank_account(acc, bik)
        assert ok is False


class TestFullPartyValidation:
    def test_valid_party_report(self):
        party_data = {
            "inn": "7707083893",
            "kpp": "770701001",
            "ogrn": "1027700132195",
            "bank_requisites": {
                "bik": "044525225",
                "account": "40702810938000012345",
            },
        }
        report = validate_party_requisites(party_data)
        assert report["valid"] is True
        assert len(report["errors"]) == 0

    def test_suggest_party_fallback(self):
        # Without DADATA_API_KEY, should validate mathematically
        res = suggest_party_by_inn("7707083893")
        assert res["valid_inn"] is True
