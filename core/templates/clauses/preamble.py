"""Legal Preamble Generator for Russian Civil Contracts."""

from __future__ import annotations
from typing import Dict, Any
from core.models.base import Party, ContractMetadata, PartyType


def get_party_role_names(contract_type: str) -> tuple[str, str]:
    """Return Russian legal role titles for Client (Party 1) and Vendor (Party 2)."""
    roles = {
        "supply": ("Покупатель", "Поставщик"),
        "services": ("Заказчик", "Исполнитель"),
        "work": ("Заказчик", "Подрядчик"),
        "nda": ("Раскрывающая сторона", "Получающая сторона"),
    }
    return roles.get(contract_type, ("Заказчик", "Исполнитель"))


def format_party_preamble(party: Party, role_title: str) -> str:
    """Format single party legal identity phrase for contract preamble."""
    if party.party_type in (PartyType.OOO, PartyType.AO):
        return (
            f"{party.full_name}, именуемое в дальнейшем «{role_title}», "
            f"в лице {party.signatory_position} {party.signatory_name}, "
            f"действующего на основании {party.signatory_basis}"
        )
    elif party.party_type == PartyType.IP:
        return (
            f"Индивидуальный предприниматель {party.signatory_name}, "
            f"именуемый в дальнейшем «{role_title}», "
            f"действующий на основании {party.signatory_basis}"
        )
    elif party.party_type == PartyType.SELF_EMPLOYED:
        return (
            f"Гражданин РФ {party.signatory_name}, "
            f"применяющий специальный налоговый режим «Налог на профессиональный доход», "
            f"именуемый в дальнейшем «{role_title}», действующий от своего имени"
        )
    else:
        return (
            f"Гражданин РФ {party.signatory_name}, "
            f"именуемый в дальнейшем «{role_title}», действующий от своего имени"
        )


def build_preamble_clauses(
    metadata: ContractMetadata,
    client: Party,
    vendor: Party,
    contract_type: str,
    contract_title: str
) -> Dict[str, Any]:
    """Generate structured header and preamble for contract."""
    client_role, vendor_role = get_party_role_names(contract_type)

    client_intro = format_party_preamble(client, client_role)
    vendor_intro = format_party_preamble(vendor, vendor_role)

    preamble_text = (
        f"{client_intro}, с одной стороны, и {vendor_intro}, с другой стороны, "
        f"совместно именуемые «Стороны», а по отдельности «Сторона», "
        f"заключили настоящий {contract_title} (далее — «Договор») о нижеследующем:"
    )

    return {
        "title": f"{contract_title.upper()} № {metadata.contract_number}",
        "city": metadata.city,
        "date": metadata.contract_date,
        "text": preamble_text,
        "client_role": client_role,
        "vendor_role": vendor_role,
    }
