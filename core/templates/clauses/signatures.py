"""Party Requisites and Signatures Builder."""

from __future__ import annotations
from typing import Dict, Any
from core.models.base import Party, BaseContract
from core.templates.clauses.preamble import get_party_role_names


def format_party_details(party: Party, role_name: str) -> Dict[str, Any]:
    """Format structured Russian legal requisites for signatures block."""
    lines = [
        f"{party.full_name}",
        f"Юр. адрес: {party.legal_address}",
    ]
    if party.actual_address and party.actual_address != party.legal_address:
        lines.append(f"Факт. адрес: {party.actual_address}")

    tax_line = f"ИНН: {party.inn}"
    if party.kpp:
        tax_line += f" / КПП: {party.kpp}"
    lines.append(tax_line)

    if party.ogrn:
        lines.append(f"ОГРН/ОГРНИП: {party.ogrn}")

    bank = party.bank_requisites
    lines.append(f"Банк: {bank.bank_name}")
    lines.append(f"БИК: {bank.bik}")
    lines.append(f"Р/с: {bank.account}")
    if bank.corr_account:
        lines.append(f"К/с: {bank.corr_account}")

    if party.phone:
        lines.append(f"Тел: {party.phone}")
    if party.email:
        lines.append(f"E-mail: {party.email}")

    return {
        "role_title": role_name.upper(),
        "party_name": party.full_name,
        "details_lines": lines,
        "signatory_position": party.signatory_position,
        "signatory_name": party.signatory_name,
        "signatory_basis": party.signatory_basis,
    }


def build_signatures_block(contract: BaseContract) -> Dict[str, Any]:
    """Generate dual-party requisites and signature block."""
    client_role, vendor_role = get_party_role_names(getattr(contract, "contract_type", "supply"))

    return {
        "client": format_party_details(contract.client, client_role),
        "vendor": format_party_details(contract.vendor, vendor_role),
    }
