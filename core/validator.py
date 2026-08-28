"""Deterministic Russian Legal & Banking Requisites Validator.

Validates INN (10/12 digits), KPP (9 chars), OGRN (13 digits), OGRNIP (15 digits),
BIK (9 digits), and Checking/Correspondent Accounts (20 digits) using official
Russian Tax Service and Central Bank checksum algorithms.
"""

from __future__ import annotations
import re
from typing import Dict, Any, Tuple


def validate_inn(inn: str | int | None) -> Tuple[bool, str]:
    """Validate Russian INN (Tax Identification Number).

    - 10 digits: Legal entities (Юридические лица)
    - 12 digits: Individual entrepreneurs and physical persons (ИП и физлица)
    """
    if not inn:
        return False, "ИНН не может быть пустым"

    inn_str = str(inn).strip()
    if not inn_str.isdigit():
        return False, "ИНН должен содержать только цифры"

    length = len(inn_str)
    digits = [int(c) for c in inn_str]

    if length == 10:
        weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        checksum = sum(d * w for d, w in zip(digits[:9], weights)) % 11 % 10
        if checksum == digits[9]:
            return True, "ИНН юридического лица корректен"
        return False, f"Неверная контрольная сумма ИНН (ожидалась {checksum}, получена {digits[9]})"

    elif length == 12:
        weights_11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        checksum_11 = sum(d * w for d, w in zip(digits[:10], weights_11)) % 11 % 10
        if checksum_11 != digits[10]:
            return False, "Неверная 11-я контрольная цифра ИНН"

        weights_12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        checksum_12 = sum(d * w for d, w in zip(digits[:11], weights_12)) % 11 % 10
        if checksum_12 != digits[11]:
            return False, "Неверная 12-я контрольная цифра ИНН"

        return True, "ИНН ИП/физического лица корректен"

    return False, f"ИНН должен состоять из 10 или 12 цифр (получено {length})"


def validate_kpp(kpp: str | None) -> Tuple[bool, str]:
    """Validate Russian KPP (Code of Reason for Registration).

    9 characters: 4 digits (tax office), 2 digits or uppercase latin/cyrillic, 3 digits.
    """
    if not kpp:
        return True, "КПП отсутствует (допустимо для ИП и физлиц)"

    kpp_str = str(kpp).strip().upper()
    if len(kpp_str) != 9:
        return False, f"КПП должен состоять из 9 символов (получено {len(kpp_str)})"

    if not re.match(r"^[0-9]{4}[0-9A-ZА-Я]{2}[0-9]{3}$", kpp_str):
        return False, "Некорректный формат КПП (формат: NNNNXXNNN)"

    return True, "КПП корректен"


def validate_ogrn(ogrn: str | int | None) -> Tuple[bool, str]:
    """Validate Russian OGRN (13 digits for LE) or OGRNIP (15 digits for IE)."""
    if not ogrn:
        return False, "ОГРН/ОГРНИП не может быть пустым"

    ogrn_str = str(ogrn).strip()
    if not ogrn_str.isdigit():
        return False, "ОГРН/ОГРНИП должен содержать только цифры"

    length = len(ogrn_str)

    if length == 13:
        num = int(ogrn_str[:12])
        control_digit = int(ogrn_str[12])
        expected = (num % 11) % 10
        if expected == control_digit:
            return True, "ОГРН юридического лица корректен"
        return False, f"Неверная контрольная цифра ОГРН (ожидалась {expected}, получена {control_digit})"

    elif length == 15:
        num = int(ogrn_str[:14])
        control_digit = int(ogrn_str[14])
        expected = (num % 13) % 10
        if expected == control_digit:
            return True, "ОГРНИП индивидуального предпринимателя корректен"
        return False, f"Неверная контрольная цифра ОГРНИП (ожидалась {expected}, получена {control_digit})"

    return False, f"ОГРН должен состоять из 13 цифр (для ЮЛ) или 15 цифр (для ИП) (получено {length})"


def validate_bik(bik: str | int | None) -> Tuple[bool, str]:
    """Validate Russian BIK (Bank Identifier Code).

    9 digits, starts with '04'.
    """
    if not bik:
        return False, "БИК не может быть пустым"

    bik_str = str(bik).strip()
    if not bik_str.isdigit():
        return False, "БИК должен содержать только цифры"

    if len(bik_str) != 9:
        return False, f"БИК должен состоять из 9 цифр (получено {len(bik_str)})"

    if not bik_str.startswith("04"):
        return False, "Российский БИК должен начинаться с 04"

    return True, "БИК корректен"


def validate_bank_account(account: str | int | None, bik: str | int | None) -> Tuple[bool, str]:
    """Validate Russian 20-digit bank checking or correspondent account against BIK.

    Uses Central Bank algorithm with weights: [7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1].
    """
    if not account:
        return False, "Номер счета не может быть пустым"

    acc_str = str(account).strip()
    if not acc_str.isdigit():
        return False, "Номер счета должен содержать только цифры"

    if len(acc_str) != 20:
        return False, f"Номер счета должен состоять ровно из 20 цифр (получено {len(acc_str)})"

    bik_valid, bik_msg = validate_bik(bik)
    if not bik_valid:
        return False, f"Невозможно проверить счет: некорректный БИК ({bik_msg})"

    bik_str = str(bik).strip()

    # If correspondent account (starts with 30101, 30102, 30103)
    if acc_str.startswith("3010"):
        bik_slice = "0" + bik_str[4:6]
    else:
        bik_slice = bik_str[6:9]

    combined = bik_slice + acc_str
    weights = [7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1]

    total = sum(int(digit) * weight for digit, weight in zip(combined, weights))
    if total % 10 == 0:
        return True, "Номер банковского счета корректен и привязан к БИК"
    return False, "Неверная контрольная сумма банковского счета для данного БИК"


def validate_party_requisites(party_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate all requisites of a party and return detailed validation report."""
    results: Dict[str, Any] = {
        "valid": True,
        "errors": {},
        "warnings": {},
        "details": {}
    }

    # INN
    inn = party_data.get("inn")
    inn_ok, inn_msg = validate_inn(inn)
    results["details"]["inn"] = {"valid": inn_ok, "message": inn_msg}
    if not inn_ok:
        results["valid"] = False
        results["errors"]["inn"] = inn_msg

    # KPP (optional if IP/person)
    kpp = party_data.get("kpp")
    kpp_ok, kpp_msg = validate_kpp(kpp)
    results["details"]["kpp"] = {"valid": kpp_ok, "message": kpp_msg}
    if not kpp_ok:
        results["valid"] = False
        results["errors"]["kpp"] = kpp_msg

    # OGRN
    ogrn = party_data.get("ogrn") or party_data.get("ogrnip")
    if ogrn:
        ogrn_ok, ogrn_msg = validate_ogrn(ogrn)
        results["details"]["ogrn"] = {"valid": ogrn_ok, "message": ogrn_msg}
        if not ogrn_ok:
            results["valid"] = False
            results["errors"]["ogrn"] = ogrn_msg

    # Bank requisites
    bank_req = party_data.get("bank_requisites") or {}
    bik = bank_req.get("bik")
    bik_ok, bik_msg = validate_bik(bik)
    results["details"]["bik"] = {"valid": bik_ok, "message": bik_msg}
    if not bik_ok:
        results["valid"] = False
        results["errors"]["bik"] = bik_msg

    account = bank_req.get("account")
    if account:
        acc_ok, acc_msg = validate_bank_account(account, bik)
        results["details"]["account"] = {"valid": acc_ok, "message": acc_msg}
        if not acc_ok:
            results["valid"] = False
            results["errors"]["account"] = acc_msg

    corr_account = bank_req.get("corr_account")
    if corr_account:
        corr_ok, corr_msg = validate_bank_account(corr_account, bik)
        results["details"]["corr_account"] = {"valid": corr_ok, "message": corr_msg}
        if not corr_ok:
            results["valid"] = False
            results["errors"]["corr_account"] = corr_msg

    return results
