"""Deterministic Russian Amount-to-Words Engine for Legal Contracts.

Provides exact grammatical declensions for numerals, rubles, and kopecks
without any external API dependencies.
"""

from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

UNITS_MASCULINE = [
    "", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"
]
UNITS_FEMININE = [
    "", "одна", "две", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"
]
TEENS = [
    "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать",
    "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"
]
TENS = [
    "", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят",
    "восемьдесят", "девяносто"
]
HUNDREDS = [
    "", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот",
    "восемьсот", "девятьсот"
]

ORDERS = [
    # (forms for 1, 2-4, 5-0), is_feminine
    (("рубль", "рубля", "рублей"), False),
    (("тысяча", "тысячи", "тысяч"), True),
    (("миллион", "миллиона", "миллионов"), False),
    (("миллиард", "миллиарда", "миллиардов"), False),
    (("триллион", "триллиона", "триллионов"), False),
]

KOPECK_FORMS = ("копейка", "копейки", "копеек")


def _get_plural_form(number: int, forms: Tuple[str, str, str]) -> str:
    """Return correct grammatical form for Russian noun based on integer value."""
    n = abs(number) % 100
    n1 = n % 10
    if 10 < n < 20:
        return forms[2]
    if 1 < n1 < 5:
        return forms[1]
    if n1 == 1:
        return forms[0]
    return forms[2]


def _triplet_to_words(triplet: int, is_feminine: bool = False) -> str:
    """Convert integer 0-999 to Russian words."""
    if triplet == 0:
        return ""

    words = []
    h = triplet // 100
    t = (triplet % 100) // 10
    u = triplet % 10

    if h > 0:
        words.append(HUNDREDS[h])

    if t == 1:
        words.append(TEENS[u])
    else:
        if t > 1:
            words.append(TENS[t])
        if u > 0:
            units_table = UNITS_FEMININE if is_feminine else UNITS_MASCULINE
            words.append(units_table[u])

    return " ".join(words)


def number_to_words_ru(number: int) -> str:
    """Convert integer to Russian words (without currency)."""
    if number == 0:
        return "ноль"

    triplets = []
    n = abs(number)
    while n > 0:
        triplets.append(n % 1000)
        n //= 1000

    words = []
    for i in range(len(triplets) - 1, -1, -1):
        triplet = triplets[i]
        if triplet == 0:
            continue

        if i < len(ORDERS):
            forms, is_fem = ORDERS[i]
            triplet_str = _triplet_to_words(triplet, is_fem)
            noun = _get_plural_form(triplet, forms) if i > 0 else ""
            if triplet_str:
                words.append(triplet_str)
            if noun:
                words.append(noun)
        else:
            words.append(str(triplet))

    result = " ".join(words).strip()
    return result if number >= 0 else "минус " + result


def amount_to_words_ru(amount: float | Decimal | int | str, capitalize_first: bool = True) -> str:
    """Convert monetary amount (in Rubles) to Russian words with rubles and kopecks.

    Example:
    125400.50 -> "Сто двадцать пять тысяч четыреста рублей 50 копеек"
    """
    dec = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    rubles = int(dec)
    kopecks = int((dec - Decimal(rubles)) * 100)

    if rubles == 0:
        rubles_str = "ноль"
    else:
        # Build rubles string
        triplets = []
        n = abs(rubles)
        while n > 0:
            triplets.append(n % 1000)
            n //= 1000

        words = []
        for i in range(len(triplets) - 1, -1, -1):
            triplet = triplets[i]
            if triplet == 0:
                continue
            forms, is_fem = ORDERS[i]
            triplet_str = _triplet_to_words(triplet, is_fem)
            noun = _get_plural_form(triplet, forms) if i > 0 else ""
            if triplet_str:
                words.append(triplet_str)
            if noun:
                words.append(noun)

        rubles_str = " ".join(words).strip()

    rubles_noun = _get_plural_form(rubles, ORDERS[0][0])
    kopecks_noun = _get_plural_form(kopecks, KOPECK_FORMS)
    kopecks_str = f"{kopecks:02d} {kopecks_noun}"

    full_text = f"{rubles_str} {rubles_noun} {kopecks_str}".strip()

    if capitalize_first and full_text:
        full_text = full_text[0].upper() + full_text[1:]

    return full_text


def format_rubles(amount: float | Decimal | int | str) -> str:
    """Format amount as standard Russian currency string: 125 400,00."""
    dec = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    parts = f"{dec:,.2f}".split(".")
    integer_part = parts[0].replace(",", " ")
    fraction_part = parts[1]
    return f"{integer_part},{fraction_part}"


def format_legal_contract_amount(
    total_amount: float | Decimal | int,
    vat_rate: int = 20,
    vat_included: bool = True,
    is_exempt_vat: bool = False
) -> str:
    """Generate complete legal wording for contract amount clause with VAT breakdown.

    Example:
    "120 000,00 (Сто двадцать тысяч) рублей 00 копеек, в том числе НДС 20% в размере 20 000,00 (Двадцать тысяч) рублей 00 копеек."
    """
    total_dec = Decimal(str(total_amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_rub = int(total_dec)
    total_kop = int((total_dec - Decimal(total_rub)) * 100)
    total_kop_noun = _get_plural_form(total_kop, KOPECK_FORMS)

    rubles_words = number_to_words_ru(total_rub)
    if rubles_words:
        rubles_words = rubles_words[0].upper() + rubles_words[1:]

    rubles_noun = _get_plural_form(total_rub, ORDERS[0][0])

    main_amount_str = (
        f"{format_rubles(total_dec)} ({rubles_words}) {rubles_noun} {total_kop:02d} {total_kop_noun}"
    )

    if is_exempt_vat or vat_rate == 0:
        return f"{main_amount_str}, НДС не облагается (в связи с применением специального налогового режима / ст. 346.11 НК РФ)"

    if vat_included:
        # VAT is included in total: VAT = Total * Rate / (100 + Rate)
        vat_dec = (total_dec * Decimal(vat_rate) / Decimal(100 + vat_rate)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        vat_rub = int(vat_dec)
        vat_kop = int((vat_dec - Decimal(vat_rub)) * 100)
        vat_kop_noun = _get_plural_form(vat_kop, KOPECK_FORMS)
        vat_words = number_to_words_ru(vat_rub)
        if vat_words:
            vat_words = vat_words[0].upper() + vat_words[1:]
        vat_rub_noun = _get_plural_form(vat_rub, ORDERS[0][0])

        vat_part_str = (
            f"в том числе НДС {vat_rate}% в размере {format_rubles(vat_dec)} "
            f"({vat_words}) {vat_rub_noun} {vat_kop:02d} {vat_kop_noun}"
        )
    else:
        # VAT is on top: VAT = Total * Rate / 100
        vat_dec = (total_dec * Decimal(vat_rate) / Decimal(100)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        vat_rub = int(vat_dec)
        vat_kop = int((vat_dec - Decimal(vat_rub)) * 100)
        vat_kop_noun = _get_plural_form(vat_kop, KOPECK_FORMS)
        vat_words = number_to_words_ru(vat_rub)
        if vat_words:
            vat_words = vat_words[0].upper() + vat_words[1:]
        vat_rub_noun = _get_plural_form(vat_rub, ORDERS[0][0])

        vat_part_str = (
            f"кроме того НДС {vat_rate}% в размере {format_rubles(vat_dec)} "
            f"({vat_words}) {vat_rub_noun} {vat_kop:02d} {vat_kop_noun}"
        )

    return f"{main_amount_str}, {vat_part_str}"
